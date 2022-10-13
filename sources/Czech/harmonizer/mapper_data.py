import datetime
from functools import partial
from hashlib import sha256

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
from neo4j import GraphDatabase
from rdflib import Namespace

import settings
from harmonizer.cache import Cache
from sources.Czech.harmonizer.Mapper import Mapper
from utils.data_transformations import building_subject, decode_hbase, building_space_subject, to_object_property, \
    location_info_subject, gross_area_subject, owner_subject, project_subject, device_subject, sensor_subject, \
    construction_element_subject, eem_subject, energy_saving_subject, fuzz_location
from utils.hbase import save_to_hbase
from utils.neo4j import create_sensor
from utils.nomenclature import harmonized_nomenclature, HARMONIZED_MODE
from utils.rdf_utils.ontology.namespaces_definition import bigg_enums, units
from utils.rdf_utils.rdf_functions import generate_rdf
from utils.rdf_utils.save_rdf import save_rdf_with_source
from utils.utils import read_config


def harmonize_building_info(data, **kwargs):
    namespace = kwargs['namespace']
    n = Namespace(namespace)
    config = kwargs['config']

    mapper = Mapper(config['source'], n)
    tax = read_config('sources/Czech/harmonizer/tax.json')

    df = pd.DataFrame(data)
    df.columns = ['Unique ID', 'Country', 'Region', 'Municipality', 'Road', 'Road Number',
                  'PostalCode',
                  'Longitude',
                  'Latitude', 'Name', 'Use Type', 'Owner', 'YearOfConstruction',
                  'GrossFloorArea',
                  'Occupancy hours', 'Number of users', 'Renewable',
                  'EnergyAudit', 'Monitoring', 'SolarPV', 'SolarPVPower', 'SolarThermal',
                  'SolarThermalPower', 'EnergyCertificate',
                  'EnergyCertificateDate', '-', 'EnergyCertificateQualification',
                  'HeatingSource',
                  'OriginalInstalledPower', 'NominalPower', 'DHW source',
                  'OriginalInstalledPowerAfter',
                  'CoolingSource', 'CoolingPower']

    df = df.applymap(decode_hbase)

    # Building
    df['building_subject'] = df['Unique ID'].apply(building_subject)

    # BuildingOwnership
    df['building_ownership_subject'] = df['Owner'].apply(lambda x: owner_subject(sha256(x.encode('utf-8')).hexdigest()))
    df['hasBuildingOwnership'] = df['building_ownership_subject'].apply(lambda x: n[x])

    # BuildingSpace
    df['building_space_subject'] = df['Unique ID'].apply(building_space_subject)
    df['building_space_uri'] = df['building_space_subject'].apply(lambda x: n[x])
    df['hasBuildingSpaceUseType'] = df['Use Type'].map(tax['hasBuildingSpaceUseType'])
    df['hasBuildingSpaceUseType'] = df['hasBuildingSpaceUseType'].replace(np.nan, "Unknown")

    df['hasBuildingSpaceUseType'] = df['hasBuildingSpaceUseType'].apply(
        lambda x: to_object_property(x, namespace=bigg_enums))

    # Location
    df['location_subject'] = df['Unique ID'].apply(location_info_subject)
    df['hasLocationInfo'] = df['location_subject'].apply(lambda x: n[x])

    mun_map = fuzz_location(location_dict=Cache.municipality_dic_GR, list_prop=['ns1:alternateName'],
                            unique_values=df['Municipality'].unique())

    df['hasAddressCity'] = df['Municipality'].map(mun_map)  # TODO: Call the correct Cache variable

    mun_map = fuzz_location(location_dict=Cache.municipality_dic_GR, list_prop=['ns1:alternateName'],
                            unique_values=df['Region'].unique())

    df['hasAddressProvince'] = df['Region'].map(mun_map)  # TODO: Call the correct Cache variable

    # Area
    df['gross_floor_area_subject'] = df['Unique ID'].apply(partial(gross_area_subject, a_source=config['source']))
    df['hasArea'] = df['gross_floor_area_subject'].apply(lambda x: n[x])

    # EnergyPerformanceCertificate
    df['EnergyCertificateDate_timestamp'] = pd.to_datetime(df['EnergyCertificateDate']).view(int) // 10 ** 9
    df['energy_performance_certificate_subject'] = df.apply(
        lambda x: f"EPC-{x['Unique ID']}-{x['EnergyCertificateDate_timestamp']}",
        axis=1)

    df['hasEPC'] = df['energy_performance_certificate_subject'].apply(lambda x: n[x])

    # AdditionalInfoEPC
    df['energy_performance_certificate_additional_subject'] = df.apply(
        lambda x: f"ADDITIONAL-EPC-{x['Unique ID']}-{x['EnergyCertificateDate_timestamp']}",
        axis=1)

    df['energy_performance_certificate_additional_uri'] = df['energy_performance_certificate_additional_subject'].apply(
        lambda x: n[x])
    translate_dict = {'Ano': True, 'Ne': False}

    df['Renewable'] = df['Renewable'].map(translate_dict)
    df['EnergyAudit'] = df['EnergyAudit'].map(translate_dict)
    df['Monitoring'] = df['Monitoring'].map(translate_dict)
    df['SolarPV'] = df['SolarPV'].map(translate_dict)
    df['SolarThermal'] = df['SolarThermal'].map(translate_dict)

    # Project
    df['project_subject'] = df['Unique ID'].apply(project_subject)
    df['hasProject'] = df['project_subject'].apply(lambda x: n[x])

    # Devices
    df['device_subject'] = df['Unique ID'].apply(partial(device_subject, source=config['source']))
    df['device_uri'] = df['device_subject'].apply(lambda x: n[x])

    # Element
    df['element_subject'] = df['Unique ID'].apply(construction_element_subject)
    df['element_uri'] = df['element_subject'].apply(lambda x: n[x])

    g = generate_rdf(mapper.get_mappings("building_info"), df)
    g.serialize('output.ttl', format="ttl")
    save_rdf_with_source(g, config['source'], config['neo4j'])


def harmonize_building_emm(data, **kwargs):
    namespace = kwargs['namespace']
    n = Namespace(namespace)
    config = kwargs['config']

    tax = read_config('sources/Czech/harmonizer/tax.json')

    df = pd.DataFrame().from_records(data)
    df.columns = ['Unique ID', 'ETM Name', 'Measure Implemented', 'Date', 'EEM Life', 'Investment', 'Subsidy',
                  'Currency Rate', 'Annual Energy Savings', 'Annual CO2 reduction', 'Comments']

    df = df.applymap(decode_hbase)

    aux = []
    for index, row in df.iterrows():
        split = row['Measure Implemented'].split('\n')
        if 'nan' in split:
            continue
        for j in split:
            x = dict(row.to_dict())
            x.update({"Measure Implemented": j.replace(';_x000D_', '')})
            aux.append(x)

    if aux:
        new_df = pd.DataFrame(aux)

        new_df['Measure Implemented'] = new_df['Measure Implemented'].map(tax['energyMeasureType'])

        # Element
        new_df['element_uri'] = new_df['Unique ID'].apply(lambda x: n[construction_element_subject(x)])

        # EnergyEfficiencyMeasure
        new_df['energy_efficiency_measure_subject'] = new_df.apply(
            lambda x: eem_subject(x['Unique ID'] + f"-{x['Measure Implemented']}"), axis=1)

        new_df['hasEnergyEfficiencyMeasureType'] = new_df['Measure Implemented'].apply(
            lambda x: to_object_property(x, namespace=bigg_enums))

        # EnergySaving
        new_df['energy_saving_subject'] = new_df['Unique ID'].apply(energy_saving_subject)
        new_df['producesSaving'] = new_df['energy_saving_subject'].apply(lambda x: n[x])

        new_df['energySavingStartDate'] = new_df['Date'].apply(
            lambda x: datetime.date(year=int(x.split('-')[0]), month=1, day=1))

        new_df['hasEnergySavingType'] = to_object_property('TotalEnergySaving', namespace=bigg_enums)

        mapper = Mapper(config['source'], n)
        g = generate_rdf(mapper.get_mappings("emm"), new_df)
        g.serialize('output.ttl', format="ttl")
        save_rdf_with_source(g, config['source'], config['neo4j'])


def harmonize_municipality_ts(data, **kwargs):
    namespace = kwargs['namespace']
    n = Namespace(namespace)
    config = kwargs['config']
    user = kwargs['user']
    freq = 'PT1M'

    hbase_conn = config['hbase_store_harmonized_data']
    neo4j_connection = config['neo4j']
    neo = GraphDatabase.driver(**neo4j_connection)

    df = pd.DataFrame(data)
    df['device_subject'] = df['Unique ID'].apply(partial(device_subject, source=config['source']))

    df = df[df['month'] < 13]

    available_years = [i for i in list(df.columns) if type(i) == int]

    unique_id = df.iloc[0]['Unique ID']
    data_type = df.iloc[0]['data_type']

    for year in available_years:
        sub_df = df[[year, 'Unique ID', 'device_subject', 'month']].copy()

        sub_df['date'] = sub_df.apply(lambda x: f"{year}/{int(x.month)}/1", axis=1)
        sub_df['ts'] = pd.to_datetime(sub_df['date'])
        sub_df['timestamp'] = sub_df['ts'].view(int) // 10 ** 9

        sub_df["bucket"] = (sub_df['timestamp'].apply(float) // settings.ts_buckets) % settings.buckets
        sub_df['start'] = sub_df['timestamp'].apply(decode_hbase)

        sub_df['end'] = sub_df['ts'] + pd.DateOffset(months=1) - pd.DateOffset(days=1)

        sub_df['end'] = sub_df['end'].view(int) // 10 ** 9
        sub_df['value'] = sub_df[year]
        sub_df['isReal'] = True

        sub_df.set_index("ts", inplace=True)
        sub_df.sort_index(inplace=True)

        dt_ini = sub_df.iloc[0].name
        dt_end = sub_df.iloc[-1].name

        device_uri = n[sub_df.iloc[0]['device_subject']]
        sensor_id = sensor_subject(config['source'], unique_id, data_type, "RAW", freq)

        sensor_uri = str(n[sensor_id])
        measurement_id = sha256(sensor_uri.encode("utf-8"))
        measurement_id = measurement_id.hexdigest()
        measurement_uri = str(n[measurement_id])

        with neo.session() as session:
            create_sensor(session, device_uri, sensor_uri, units["KiloW-HR"],
                          bigg_enums[data_type], bigg_enums.TrustedModel,
                          measurement_uri, False,
                          False, False, freq, "SUM", dt_ini, dt_end, settings.namespace_mappings)

            sub_df['listKey'] = measurement_id

            device_table = harmonized_nomenclature(mode=HARMONIZED_MODE.ONLINE, data_type=data_type, R=False,
                                                   C=False, O=False, aggregation_function="SUM", freq=freq, user=user)

            save_to_hbase(sub_df.to_dict(orient="records"),
                          device_table,
                          hbase_conn,
                          [("info", ['end', 'isReal']), ("v", ['value'])],
                          row_fields=['bucket', 'listKey', 'start'])

            period_table = harmonized_nomenclature(mode=HARMONIZED_MODE.BATCH, data_type=data_type, R=False,
                                                   C=False, O=False, aggregation_function="SUM", freq=freq, user=user)

            save_to_hbase(sub_df.to_dict(orient="records"),
                          period_table, hbase_conn,
                          [("info", ['end', 'isReal']), ("v", ['value'])],
                          row_fields=['bucket', 'start', 'listKey'])


def harmonize_region_ts(data, **kwargs):
    namespace = kwargs['namespace']
    n = Namespace(namespace)
    config = kwargs['config']
    user = kwargs['user']
    freq = 'PT1M'

    hbase_conn = config['hbase_store_harmonized_data']
    neo4j_connection = config['neo4j']
    neo = GraphDatabase.driver(**neo4j_connection)

    df = pd.DataFrame(data)
    df.drop('celkem', axis=1, inplace=True)
    df.columns = ['DataType', 'Year', 1, 2, 3, 4, 5, 6, 7, 8,
                  9, 10, 11, 12, 'Unit', 'Unique ID']

    tax = read_config('sources/Czech/harmonizer/tax.json')

    df['DataType'] = df['DataType'].map(tax['consumptionType'])
    df = df[df['DataType'].notna()]

    df['device_subject'] = df['Unique ID'].apply(partial(device_subject, source=config['source']))

    for index, row in df.iterrows():
        aux = []
        unique_id = row['Unique ID']
        data_type = row['DataType']

        for x in range(1, 13):
            date = datetime.datetime(year=row['Year'], month=x, day=1)
            date_end = date + relativedelta(month=1) - datetime.timedelta(days=1)
            value = row[x]
            aux.append(
                {"date": date, "date_end": date_end, "value": value, "Unique ID": unique_id, 'DataType': data_type,
                 'device_subject': row['device_subject']})

        sub_df = pd.DataFrame(aux)

        sub_df['ts'] = sub_df['date']
        sub_df['timestamp'] = sub_df['ts'].view(int) // 10 ** 9
        sub_df["bucket"] = (sub_df['timestamp'].apply(float) // settings.ts_buckets) % settings.buckets
        sub_df['start'] = sub_df['timestamp'].apply(decode_hbase)
        sub_df['end'] = sub_df['date_end'].view(int) // 10 ** 9
        sub_df['isReal'] = True

        sub_df.set_index("ts", inplace=True)
        sub_df.sort_index(inplace=True)

        dt_ini = sub_df.iloc[0].name
        dt_end = sub_df.iloc[-1].name

        device_uri = n[sub_df.iloc[0]['device_subject']]
        sensor_id = sensor_subject(config['source'], unique_id, data_type, "RAW", freq)

        sensor_uri = str(n[sensor_id])
        measurement_id = sha256(sensor_uri.encode("utf-8"))
        measurement_id = measurement_id.hexdigest()
        measurement_uri = str(n[measurement_id])

        with neo.session() as session:
            create_sensor(session, device_uri, sensor_uri, units["KiloW-HR"],
                          bigg_enums[data_type], bigg_enums.TrustedModel,
                          measurement_uri, False,
                          False, False, freq, "SUM", dt_ini, dt_end, settings.namespace_mappings)

        sub_df['listKey'] = measurement_id

        device_table = harmonized_nomenclature(mode=HARMONIZED_MODE.ONLINE, data_type=data_type, R=False,
                                               C=False, O=False, aggregation_function="SUM", freq=freq, user=user)

        save_to_hbase(sub_df.to_dict(orient="records"),
                      device_table,
                      hbase_conn,
                      [("info", ['end', 'isReal']), ("v", ['value'])],
                      row_fields=['bucket', 'listKey', 'start'])

        period_table = harmonized_nomenclature(mode=HARMONIZED_MODE.BATCH, data_type=data_type, R=False,
                                               C=False, O=False, aggregation_function="SUM", freq=freq, user=user)

        save_to_hbase(sub_df.to_dict(orient="records"),
                      period_table, hbase_conn,
                      [("info", ['end', 'isReal']), ("v", ['value'])],
                      row_fields=['bucket', 'start', 'listKey'])
