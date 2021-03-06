import hashlib
from datetime import timedelta

import numpy as np
import pandas as pd
import rdflib
from neo4j import GraphDatabase
from rdflib import Namespace
from thefuzz import process

import settings
from harmonizer.cache import Cache
from sources.Bulgaria.constants import enum_energy_efficiency_measurement_type, enum_energy_saving_type, eem_headers
from sources.Bulgaria.harmonizer.Mapper import Mapper
from utils.data_transformations import *
from utils.hbase import save_to_hbase
from utils.neo4j import create_sensor
from utils.rdf_utils.ontology.namespaces_definition import bigg_enums, units
from utils.rdf_utils.rdf_functions import generate_rdf
from utils.rdf_utils.save_rdf import save_rdf_with_source


def set_taxonomy(df):
    df['type_of_building'] = df['type_of_building'].str.strip()
    building_type_taxonomy = get_taxonomy_mapping(
        taxonomy_file="sources/Bulgaria/harmonizer/TAX_BULGARIA.xlsx",
        default="Other")
    df['buildingSpaceUseType'] = df['type_of_building'].map(building_type_taxonomy).apply(partial(to_object_property,
                                                                                              namespace=bigg_enums))

def set_municipality(df):
    province_dic = Cache.province_dic_BG
    province_fuzz = partial(fuzzy_dictionary_match,
                            map_dict=fuzz_params(
                                province_dic,
                                ['ns1:name']
                            ),
                            default=None
                            )
    unique_province = df['municipality'].unique()
    province_map = {k: province_fuzz(k) for k in unique_province}
    df.loc[:, 'hasAddressProvince'] = df['municipality'].map(province_map)


def clean_dataframe_building_info(df_orig, source):
    df = df_orig.copy(deep=True)
    df['subject'] = df['filename'] + '-' + df['id'].astype(str)
    df['organization_subject'] = df['subject'].apply(building_department_subject)
    df['building_subject'] = df['subject'].apply(building_subject)
    df['building_name'] = df.apply(lambda x: f"{x.name}-{x.municipality}-{x.type_of_building}", axis=1)

    df['location_subject'] = df['subject'].apply(location_info_subject)
    df['epc_date_before'] = pd.to_datetime(df['epc_date']) - timedelta(days=365)
    df['epc_before_subject'] = df['subject'].apply(lambda x: x + '-before').apply(epc_subject)
    df['epc_after_subject'] = df['subject'].apply(lambda x: x + '-after').apply(epc_subject)

    df['building_space_subject'] = df['subject'].apply(building_space_subject)
    df['gross_floor_area_subject'] = df['subject'].apply(partial(gross_area_subject, a_source=source))
    df['element_subject'] = df['subject'].apply(construction_element_subject)
    df['device_subject'] = df['subject'].apply(partial(device_subject, source=source))
    df['project_subject'] = df['subject'].apply(project_subject)
    return df[['subject', 'organization_subject', 'building_subject', 'building_name', 'location_subject',
               'hasAddressProvince', 'epc_date_before', 'epc_before_subject', 'epc_energy_class_before',
               'annual_energy_consumption_before_total_consumption', 'epc_after_subject',
               'epc_energy_class_after', 'project_subject', 'epc_date', 'total_savings_Investments',
               'building_space_subject', 'buildingSpaceUseType', 'gross_floor_area_subject', 'gross_floor_area',
               'element_subject', 'device_subject',
               ]]


def clean_dataframe_eem_savings(df_orig, eems_parted, start_column):
    df = df_orig.copy(deep=True)
    df['subject'] = df['filename'] + '-' + df['id'].astype(str)
    df['element_subject'] = df['subject'].apply(construction_element_subject)
    df['epc_date_before'] = pd.to_datetime(df['epc_date']) - timedelta(days=365)
    saving_columns = []
    for i, eem_type in enumerate(eems_parted):
        list_i = i + start_column
        df[f"eem_{list_i}_subject"] = df['subject'].apply(lambda x: f"{x}-{eem_type}").apply(eem_subject)
        for j, e_saving_type in enumerate(enum_energy_saving_type):
            df_t = df['subject'].apply(lambda x: f"{x}-{eem_type}-{e_saving_type}").apply(energy_saving_subject)
            df_t.name = f"energy_saving_{list_i}_{j}_subject"
            saving_columns.append(df_t)
    df = pd.concat([df] + saving_columns, axis=1)
    return df[['subject', 'element_subject', 'epc_date_before', 'epc_date'] +
              [x for x in df.columns if re.match("eem_.*_subject", x)] +
              [x for x in df.columns if re.match("measurement_.*", x)] +
              [x for x in df.columns if re.match("energy_saving_.*_subject", x)]]


def clean_dataframe_project(df_orig):
    df = df_orig.copy(deep=True)
    df['subject'] = df['filename'] + '-' + df['id'].astype(str)
    df['project_subject'] = df['subject'].apply(project_subject)
    df['epc_date_before'] = pd.to_datetime(df['epc_date']) - timedelta(days=365)
    for i, eem_type in enumerate(enum_energy_efficiency_measurement_type):
        df[f"eem_{i}_subject"] = df['subject'].apply(lambda x: f"{x}-{eem_type}").apply(eem_subject)
    for saving_type in enum_energy_saving_type:
        df[f'project_energy_saving_subject_{saving_type}'] = df['subject']\
            .apply(lambda x: f"{x}-project-{saving_type}").apply(energy_saving_subject)
    return df[['subject', 'project_subject', 'epc_date_before', 'epc_date'] +
              [x for x in df.columns if re.match("eem_.*_subject", x)] +
              [x for x in df.columns if re.match("total_.*", x)] +
              [x for x in df.columns if re.match("energy_saving_.*_subject", x)] +
              [x for x in df.columns if re.match("project_energy_saving_subject_.*", x)]]



def harmonize_static(data, **kwargs):
    namespace = kwargs['namespace']
    n = Namespace(namespace)
    config = kwargs['config']
    df = pd.DataFrame.from_records(data)
    df = df.applymap(decode_hbase)
    set_taxonomy(df)
    set_municipality(df)
    mapper = Mapper(config['source'], n)
    df_building = clean_dataframe_building_info(df, config['source'])
    g = generate_rdf(mapper.get_mappings("building_info"), df_building)
    save_rdf_with_source(g, config['source'], config['neo4j'])
    parts_eem = 2
    parts_saving = 2
    start_column_eem = 0
    for chunk in range(parts_eem):
        k, m = divmod(len(enum_energy_efficiency_measurement_type), parts_eem)
        eems_parted = [enum_energy_efficiency_measurement_type[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in
                       range(parts_eem)]
        df_eem = clean_dataframe_eem_savings(df, eems_parted[chunk], start_column_eem)
        start_column_saving = 0
        for chunk_saving in range(parts_saving):
            k, m = divmod(len(enum_energy_saving_type), parts_saving)
            saving_parted = [enum_energy_saving_type[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(parts_saving)]
            mapper.select_chunk(eems_parted[chunk], start_column_eem, saving_parted[chunk_saving], start_column_saving)
            g = generate_rdf(mapper.get_mappings("eem_savings"), df_eem)
            try:
                save_rdf_with_source(g, config['source'], config['neo4j'])
            except Exception:
                g.serialize("error.ttl")
                raise Exception("File in error.ttl")
            start_column_saving += len(saving_parted[chunk_saving])
        start_column_eem += len(eems_parted[chunk])
        print("FIN")
    df_project = clean_dataframe_project(df)
    g = generate_rdf(mapper.get_mappings("project_info"), df_project)
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
    # TODO: municipality and building_type taxonomy
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
