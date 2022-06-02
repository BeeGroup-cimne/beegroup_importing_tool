import hashlib
from datetime import timedelta

import numpy as np
import pandas as pd
import rdflib
from neo4j import GraphDatabase
from rdflib import Namespace
from thefuzz import process

import settings
from sources.Bulgaria.constants import enum_energy_efficiency_measurement_type, enum_energy_saving_type, eem_headers
from sources.Bulgaria.harmonizer.Mapper import Mapper
from utils.data_transformations import sensor_subject, to_object_property
from utils.hbase import save_to_hbase
from utils.neo4j import create_sensor
from utils.rdf_utils.ontology.namespaces_definition import bigg_enums, units
from utils.rdf_utils.rdf_functions import generate_rdf
from utils.rdf_utils.save_rdf import save_rdf_with_source


def set_taxonomy(df):
    df['type_of_building'] = df['type_of_building'].str.strip()
    tax_df = pd.read_excel("data/tax/TAX_BULGARIA.xlsx", header=None, names=["Source", "Taxonomy"], sheet_name='Hoja1')
    tax_dict = {}
    for i in tax_df.to_dict(orient="records"):
        tax_dict.update({i['Source']: to_object_property(i['Taxonomy'], namespace=bigg_enums)})

    df['type_of_building'] = df['type_of_building'].map(tax_dict)
    return df


def set_municipality(df, label='municipality', predicates=None,
                     dictionary_ttl_file="utils/rdf_utils/ontology/dictionaries/municipality.ttl"):
    if predicates is None:
        predicates = ['ns1:name']

    df[label] = df[label].str.strip()
    unique_municipalities = list(df[label].unique())

    dicty = rdflib.Graph()
    dicty.load(dictionary_ttl_file, format="ttl")
    query = f"""SELECT ?s ?obj WHERE{{ {" UNION ".join([f"{{ ?s {p} ?obj }}" for p in predicates])} }}"""
    obj = dicty.query(query)
    map_dict = {o[1]: o[0] for o in obj}

    mapping_dict = {}
    for i in unique_municipalities:
        match = process.extractOne(i, list(map_dict.keys()), score_cutoff=90)
        if match:
            mapping_dict.update({i: map_dict[match[0]]})

    df['municipality'] = df['municipality'].map(mapping_dict)
    return df


def harmonize_static(data, **kwargs):
    namespace = kwargs['namespace']
    n = Namespace(namespace)
    config = kwargs['config']

    df = set_taxonomy(pd.DataFrame().from_records(data))
    df = set_municipality(df)

    df['subject'] = df['filename'] + '-' + df['id'].astype(str)

    df['organization_subject'] = 'ORGANIZATION-' + df['subject']

    df['building_subject'] = 'BUILDING-' + df['subject']
    df['building_name'] = df['subject'] + '-' + df['municipality'] + '-' + df['type_of_building']

    df['location_subject'] = 'LOCATION-' + df['subject']

    df['epc_date_before'] = df['epc_date'] - timedelta(days=365)
    df['epc_before_subject'] = 'EPC-' + df['subject'] + '-' + df['epc_energy_class_before']
    df['epc_after_subject'] = 'EPC-' + df['subject'] + '-' + df['epc_energy_class_after']

    df['building_space_subject'] = 'BUILDINGSPACE-' + df['subject']
    df['building_space_use_type_subject'] = 'BUILDING-SPACE-USE-TYPE-' + df['subject']

    df['gross_floor_area_subject'] = 'AREA-GrossFloorArea-' + config['source'] + '-' + df['subject']
    df['element_subject'] = 'ELEMENT-' + df['subject']

    df['device_subject'] = 'DEVICE-' + config['source'] + '-' + df['subject']

    for i in range(len(enum_energy_efficiency_measurement_type)):
        df[f"eem_{i}_subject"] = 'EEM-' + df['subject'] + '-' + enum_energy_efficiency_measurement_type[i]
        df[f"emm_{i}_type"] = enum_energy_efficiency_measurement_type[i]

        for j in range(len(enum_energy_saving_type)):
            df[f"energy_saving_{i}_{j}_subject"] = 'EnergySaving-' + df['subject'] + '-' + \
                                                   enum_energy_efficiency_measurement_type[
                                                       i] + '-' + enum_energy_saving_type[j]
            df[f"energy_saving_{i}_{j}_type"] = enum_energy_saving_type[j]

    df.dropna(subset=['epc_before_subject'], inplace=True)

    mapper = Mapper(config['source'], n)
    g = generate_rdf(mapper.get_mappings("all"), df)

    g.serialize('output.ttl', format="ttl")
    save_rdf_with_source(g, config['source'], config['neo4j'])


def harmonize_ts(data, **kwargs):
    namespace = kwargs['namespace']
    user = kwargs['user']
    n = Namespace(namespace)
    config = kwargs['config']
    freq = 'PT1Y'

    df = pd.DataFrame.from_records(data)
    df['subject'] = df['filename'] + '-' + df['id'].astype(str)
    df['epc_date_before'] = df['epc_date'] - timedelta(days=365)
    df['device_subject'] = 'DEVICE-' + config['source'] + '-' + df['subject']

    neo4j_connection = config['neo4j']

    measured_property_list = ['EnergyConsumptionOil', 'EnergyConsumptionCoal',
                              'EnergyConsumptionGas', 'EnergyConsumptionOthers',
                              'EnergyConsumptionDistrictHeating',
                              'EnergyConsumptionGridElectricity', 'EnergyConsumptionTotal']

    measured_property_df = ['annual_energy_consumption_before_liquid_fuels',
                            'annual_energy_consumption_before_hard_fuels',
                            'annual_energy_consumption_before_gas', 'annual_energy_consumption_before_others',
                            'annual_energy_consumption_before_heat_energy',
                            'annual_energy_consumption_before_electricity',
                            'annual_energy_consumption_before_total_consumption']

    neo = GraphDatabase.driver(**neo4j_connection)
    hbase_conn2 = config['hbase_store_harmonized_data']

    with neo.session() as session:
        for index, row in df.iterrows():
            device_uri = str(n[row['device_subject']])

            for i in range(len(measured_property_list)):
                sensor_id = sensor_subject(config['source'], row['subject'], measured_property_list[i], "RAW",
                                           freq)
                sensor_uri = str(n[sensor_id])
                measurement_id = hashlib.sha256(sensor_uri.encode("utf-8"))
                measurement_id = measurement_id.hexdigest()
                measurement_uri = str(n[measurement_id])
                create_sensor(session, device_uri, sensor_uri, units["KiloW-HR"],
                              bigg_enums[measured_property_list[i]], bigg_enums.TrustedModel,
                              measurement_uri,
                              False, False, freq, "SUM", row['epc_date_before'], row['epc_date'])
                reduced_df = df[['subject', measured_property_df[i],
                                 'epc_date',
                                 'epc_date_before']]

                reduced_df['listKey'] = measurement_id
                reduced_df['isRead'] = True
                reduced_df['bucket'] = (df['epc_date_before'].values.astype(np.int64) // 10 ** 9) % settings.buckets
                reduced_df['start'] = (df['epc_date_before'].values.astype(np.int64) // 10 ** 9) % settings.buckets
                reduced_df['end'] = (df['epc_date'].values.astype(np.int64) // 10 ** 9) % settings.buckets

                reduced_df.rename(
                    columns={measured_property_df[i]: "value"},
                    inplace=True)

                device_table = f"harmonized_online_{measured_property_list[i]}_100_SUM_{freq}_{user}"

                save_to_hbase(reduced_df.to_dict(orient="records"), device_table, hbase_conn2,
                              [("info", ['end', 'isReal']), ("v", ['value'])],
                              row_fields=['bucket', 'listKey', 'start'])

                period_table = f"harmonized_batch_{measured_property_list[i]}_100_SUM_{freq}_{user}"

                save_to_hbase(reduced_df.to_dict(orient="records"), period_table, hbase_conn2,
                              [("info", ['end', 'isReal']), ("v", ['value'])],
                              row_fields=['bucket', 'start', 'listKey'])


def harmonize_detail(data, **kwargs):
    namespace = kwargs['namespace']
    n = Namespace(namespace)
    config = kwargs['config']

    df = pd.DataFrame(data)

    # Transformations
    df.rename(columns={"location_municipality": "municipality", "area_gross_floor_area": "gross_floor_area"},
              inplace=True)

    df['epc_date'] = pd.to_datetime(df['epc_date'])
    df['epc_date_before'] = df['epc_date'] - timedelta(days=365)
    df['annual_energy_consumption_before_total_consumption'] = df['consumption_11_type']

    # Subjects
    df['subject'] = df['epc_id']
    df['organization_subject'] = 'ORGANIZATION-' + df['subject']
    df['building_subject'] = 'BUILDING-' + df['subject']
    df['building_name'] = df['subject'] + '-' + df['municipality'] + '-' + df['building_type']
    df['location_subject'] = 'LOCATION-' + df['subject']

    df['epc_before_subject'] = 'EPC-' + df['subject'] + '-' + df['epc_energy_class_before']
    df['epc_after_subject'] = 'EPC-' + df['subject'] + '-' + df['epc_energy_class_after']

    df['building_space_subject'] = 'BUILDINGSPACE-' + df['subject']
    df['gross_floor_area_subject'] = 'AREA-GrossFloorArea-' + config['source'] + '-' + df['subject']

    df['element_subject'] = 'ELEMENT-' + df['subject']

    df['device_subject'] = 'DEVICE-' + config['source'] + '-' + df['subject']

    for i in range(len(enum_energy_efficiency_measurement_type)):
        for j in range(len(eem_headers)):
            if j == 0:
                df[f"measurement_{i}_{eem_headers[j]}"] = df[f"measure_{i}_0"] + df[f"measure_{i}_1"]

            if j == 1:
                df[f"measurement_{i}_{eem_headers[j]}"] = df[f"measure_{i}_3"]

            if j == 2:
                df[f"measurement_{i}_{eem_headers[j]}"] = df[f"measure_{i}_4"] + df[f"measure_{i}_5"]

            if j == 3:
                df[f"measurement_{i}_{eem_headers[j]}"] = df[f"measure_{i}_8"] + df[
                    f"measure_{i}_2"] + df[
                                                              f"measure_{i}_6"] + df[f"measure_{i}_7"]

            if j == 4:
                df[f"measurement_{i}_{eem_headers[j]}"] = df[f"measure_{i}_9"]

            if j == 5:
                df[f"measurement_{i}_{eem_headers[j]}"] = df[f"measure_{i}_10"]

            if j == 6:
                df[f"measurement_{i}_{eem_headers[j]}"] = df[f"measure_{i}_11"]

    for i in range(len(enum_energy_efficiency_measurement_type)):
        df[f"eem_{i}_subject"] = 'EEM-' + df['subject'] + '-' + enum_energy_efficiency_measurement_type[i]
        df[f"emm_{i}_type"] = enum_energy_efficiency_measurement_type[i]

        for j in range(len(enum_energy_saving_type)):
            df[f"energy_saving_{i}_{j}_subject"] = 'EnergySaving-' + df['subject'] + '-' + \
                                                   enum_energy_efficiency_measurement_type[
                                                       i] + '-' + enum_energy_saving_type[j]

    mapper = Mapper(config['source'], n)
    g = generate_rdf(mapper.get_mappings("all"), df)

    g.serialize('output.ttl', format="ttl")
    save_rdf_with_source(g, config['source'], config['neo4j'])
