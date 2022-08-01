from functools import partial
from functools import partial
from hashlib import sha256

import numpy as np
import pandas as pd
from rdflib import Namespace

import settings
from sources.Czech.harmonizer.Mapper import Mapper
from utils.data_transformations import building_subject, decode_hbase, building_space_subject, to_object_property, \
    location_info_subject, gross_area_subject, owner_subject, project_subject, device_subject, sensor_subject
from utils.rdf_utils.ontology.namespaces_definition import bigg_enums
from utils.rdf_utils.rdf_functions import generate_rdf
from utils.utils import read_config


def harmonize_building_info(data, **kwargs):
    # namespace = 'https://czech.cz#'
    # config = read_config('config.json')
    # config.update({"source": "czech"})
    # user = "czech"

    namespace = kwargs['namespace']
    user = kwargs['user']
    n = Namespace(namespace)
    config = kwargs['config']

    mapper = Mapper(config['source'], n)
    tax = read_config('tax.json')

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
    df['hasBuildingSpaceUseType'] = df['Use Type'].map(tax['hasBuildingSpaceUseType'])
    df['hasBuildingSpaceUseType'] = df['hasBuildingSpaceUseType'].replace(np.nan, "Unknown")

    df['hasBuildingSpaceUseType'] = df['hasBuildingSpaceUseType'].apply(
        lambda x: to_object_property(x, namespace=bigg_enums))

    # Location
    df['location_subject'] = df['Unique ID'].apply(location_info_subject)
    df['hasLocationInfo'] = df['location_subject'].apply(lambda x: n[x])
    # df['hasAddressCity'] = df['Unique ID'].apply(location_info_subject)
    # df['hasAddressProvince'] = df['Unique ID'].apply(location_info_subject)

    # Area
    df['gross_floor_area_subject'] = df['Unique ID'].apply(partial(gross_area_subject, a_source=config['source']))
    df['hasArea'] = df['gross_floor_area_subject'].apply(lambda x: n[x])

    # EnergyPerformanceCertificate
    df['EnergyCertificateDate_timestamp'] = pd.to_datetime(df['EnergyCertificateDate']).view(int) // 10 ** 9
    df['energy_performance_certificate_subject'] = df.apply(
        lambda x: f"EPC-{x['Unique ID']}-{x['EnergyCertificateDate_timestamp']}",
        axis=1)

    df['hasEPC'] = df['energy_performance_certificate_subject'].apply(lambda x: n[x])

    # Project
    df['project_subject'] = df['Unique ID'].apply(project_subject)
    df['hasProject'] = df['project_subject'].apply(lambda x: n[x])

    # Devices
    df['device_subject'] = df['subject'].apply(partial(device_subject, source=config['source']))

    g = generate_rdf(mapper.get_mappings("building_info"), df)
    g.serialize('output.ttl', format="ttl")
    # save_rdf_with_source(g, config['source'], config['neo4j'])


def harmonize_building_emm(data, **kwargs):
    namespace = kwargs['namespace']
    user = kwargs['user']
    n = Namespace(namespace)
    config = kwargs['config']

    mapper = Mapper(config['source'], n)
    tax = read_config('tax.json')

    df = pd.DataFrame(data)
    df.columns = ['Unique ID', 'ETM Name', 'Measure Implemented', 'Date', 'EEM Life', 'Investment', 'Subsidy',
                  'Currency Rate', 'Annual Energy Savings', 'Annual CO2 reduction', 'Comments']

    df = df.applymap(decode_hbase)

    df['Measure Implemented'].apply(lambda x: len(x.split(";"))).max()
    # TODO:


def harmonize_municipality_gas(data, **kwargs):
    pass


def harmonize_municipality_ts(data, **kwargs):
    namespace = kwargs['namespace']
    user = kwargs['user']
    n = Namespace(namespace)
    config = kwargs['config']

    df = pd.DataFrame(data)
    df['device_subject'] = df['subject'].apply(partial(device_subject, source=config['source']))
    df_c = df.iloc[:-1, :].copy()  # drop last row

    available_years = [i for i in list(df_c.columns) if type(i) == int]

    unique_id = df.iloc[0]['Unique ID']

    for year in available_years:
        sub_df = df_c[[year, 'Unique ID']].copy()
        sub_df.dropna(inplace=True)

        sub_df['date'] = sub_df.apply(lambda x: f"{year}/{int(x.name) + 1}/1", axis=1)
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

        dt_ini = sub_df.iloc[0]
        dt_end = sub_df.iloc[-1]

        device_uri = n[sub_df.iloc[0]['device_subject']]
        sensor_id = sensor_subject(config['source'], unique_id, "EnergyConsumptionGas", "RAW", "")

        sensor_uri = str(n[sensor_id])
        measurement_id = hashlib.sha256(sensor_uri.encode("utf-8"))
        measurement_id = measurement_id.hexdigest()
        measurement_uri = str(n[measurement_id])

        final_df = sub_df[['ts', 'bucket', 'CUPS', 'start', 'end', 'value', 'isReal']]


def harmonize_region_ts(data, **kwargs):
    namespace = kwargs['namespace']
    user = kwargs['user']
    n = Namespace(namespace)
    config = kwargs['config']
    print(data)
