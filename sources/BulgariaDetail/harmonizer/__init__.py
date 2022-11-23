import hashlib
from datetime import timedelta

from neo4j import GraphDatabase
from rdflib import Namespace
from slugify import slugify

import settings
from sources.Bulgaria.constants import enum_energy_efficiency_measurement_type, enum_energy_saving_type, eem_headers
from sources.Bulgaria.harmonizer.Mapper import Mapper
from sources.Bulgaria.harmonizer.mapper_buildings import set_source_id
from sources.BulgariaDetail.utils import set_taxonomy, set_municipality
from utils.data_transformations import *
from utils.hbase import save_to_hbase
from utils.neo4j import create_sensor
from utils.nomenclature import harmonized_nomenclature
from utils.rdf_utils.ontology.namespaces_definition import bigg_enums, units
from utils.rdf_utils.rdf_functions import generate_rdf
from utils.rdf_utils.save_rdf import save_rdf_with_source, link_devices_with_source


def clean_general(df, kwargs):
    df = df.applymap(decode_hbase)
    df['building_type'] = df['building_type'].str.strip()

    df.rename(
        columns={'building_type': 'type_of_building', 'location_municipality': 'municipality',
                 'area_gross_floor_area': 'gross_floor_area'},
        inplace=True)

    set_source_id(df, kwargs['user'], kwargs['config']['neo4j'])
    set_taxonomy(df, 'municipality')
    set_municipality(df, 'municipality')

    df['subject'] = df['epc_id']

    df['epc_date'] = pd.to_datetime(df['epc_date'], infer_datetime_format=True)
    df['epc_date_before'] = df['epc_date'] - timedelta(days=365)
    df['epc_date'] = (df['epc_date'].astype('datetime64')).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    df['epc_date_before'] = (df['epc_date_before'].astype('datetime64')).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    df['epc_before_subject'] = df['subject'].apply(lambda x: x + '-before').apply(epc_subject)
    df['epc_after_subject'] = df['subject'].apply(lambda x: x + '-after').apply(epc_subject)


def clean_building_info(df, source):
    df['location_org_subject'] = df['municipality'].apply(slugify).apply(building_department_subject)
    df['organization_subject'] = df['subject'].apply(building_department_subject)
    df['building_subject'] = df['subject'].apply(building_subject)
    df['building_name'] = df.apply(lambda x: f"{x.municipality}:{x.type_of_building}", axis=1)
    df['building_id'] = df['subject']
    df['location_subject'] = df['subject'].apply(location_info_subject)

    df['building_space_subject'] = df['subject'].apply(building_space_subject)
    df['gross_floor_area_subject'] = df['subject'].apply(partial(gross_area_subject, a_source=source))
    df['element_subject'] = df['subject'].apply(construction_element_subject)
    df['device_subject'] = df['subject'].apply(partial(device_subject, source=source))
    df['utility_subject'] = df['subject'].apply(delivery_subject)
    df['project_subject'] = df['subject'].apply(project_subject)

    df['annual_energy_consumption_before_total_consumption'] = df['epc_specific_energy_consumption_before (kWh/m2)']
    df['total_savings_Investments'] = df['total_annual_savings_11']

    return df[['location_org_subject', 'municipality', 'organization_subject',
               'building_name',
               'building_subject', 'building_id', 'location_subject', 'hasAddressCity',
               'building_space_subject',
               'buildingSpaceUseType', 'gross_floor_area_subject', 'epc_before_subject', 'epc_date_before',
               'epc_energy_class_before', 'annual_energy_consumption_before_total_consumption',
               'epc_after_subject',
               'epc_date', 'epc_energy_class_after', 'project_subject', 'total_savings_Investments',
               'element_subject',
               'device_subject', 'utility_subject', 'subject'
               ]]


def clean_project(df):
    df['project_subject'] = df['subject'].apply(project_subject)

    for i, eem_type in enumerate(enum_energy_efficiency_measurement_type):
        df[f"eem_{i}_subject"] = df['subject'].apply(lambda x: f"{x}-{eem_type}").apply(eem_subject)
    for saving_type in enum_energy_saving_type:
        df[f'project_energy_saving_subject_{saving_type}'] = df['subject'] \
            .apply(lambda x: f"{x}-project-{saving_type}").apply(energy_saving_subject)
    return df[['subject', 'project_subject', 'epc_date_before', 'epc_date'] +
              [x for x in df.columns if re.match("eem_.*_subject", x)] +
              [x for x in df.columns if re.match("total_.*", x)] +
              [x for x in df.columns if re.match("energy_saving_.*_subject", x)] +
              [x for x in df.columns if re.match("project_energy_saving_subject_.*", x)]]


def clean_eem_savings(df, source):
    df['element_subject'] = df['subject'].apply(construction_element_subject)
    df['device_subject'] = df['subject'].apply(partial(device_subject, source=source))

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

    return df[['subject', 'element_subject', 'device_subject', 'epc_date_before', 'epc_date'] +
              [x for x in df.columns if re.match("eem_.*_subject", x)] +
              [x for x in df.columns if re.match("measurement_.*", x)] +
              [x for x in df.columns if re.match("energy_saving_.*_subject", x)]]


def harmonize_eem_es(df, mapper, config):
    parts_eem = 2
    parts_saving = 2
    start_column_eem = 0
    for chunk in range(parts_eem):
        k, m = divmod(len(enum_energy_efficiency_measurement_type), parts_eem)
        eems_parted = [enum_energy_efficiency_measurement_type[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in
                       range(parts_eem)]
        start_column_saving = 0
        for chunk_saving in range(parts_saving):
            k, m = divmod(len(enum_energy_saving_type), parts_saving)
            saving_parted = [enum_energy_saving_type[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in
                             range(parts_saving)]
            mapper.select_chunk(eems_parted[chunk], start_column_eem, saving_parted[chunk_saving], start_column_saving)
            g = generate_rdf(mapper.get_mappings("eem_savings"), df)
            g.serialize('output.ttl', format='ttl')
            try:
                save_rdf_with_source(g, config['source'], config['neo4j'])
            except Exception:
                g.serialize("error.ttl")
                raise Exception("File in error.ttl")
            start_column_saving += len(saving_parted[chunk_saving])
        start_column_eem += len(eems_parted[chunk])


def clean_ts(df, source):
    df['device_subject'] = df['subject'].apply(partial(device_subject, source=source))
    return df[['subject', 'device_subject'] + [x for x in df.columns if re.match("consumption.*", x)]]


def is_str(value):
    return int(value) if value is not None and value.isnumeric() else 0


def harmonize_ts(df, config, n, user, freq='PT1Y'):
    neo4j_connection = config['neo4j']
    neo = GraphDatabase.driver(**neo4j_connection)
    hbase_conn2 = config['hbase_store_harmonized_data']
    df_ts = clean_ts(df, config['source'])

    for index, row in df_ts.iterrows():
        pair_values = []
        pair_values.append(
            (is_str(row.get('consumption_0')) + is_str(row.get('consumption_1')), 'EnergyConsumptionOil'))

        pair_values.append((is_str(row.get('consumption_3')), 'EnergyConsumptionCoal'))

        pair_values.append(
            (is_str(row.get('consumption_4')) + is_str(row.get('consumption_5')), 'EnergyConsumptionGas'))

        pair_values.append(
            (is_str(row.get('consumption_2')) + is_str(row.get('consumption_6')) + is_str(
                row.get('consumption_7')) + is_str(row.get('consumption_8')), 'EnergyConsumptionOthers'))

        pair_values.append((is_str(row.get('consumption_9')), 'EnergyConsumptionDistrictHeating'))
        pair_values.append((is_str(row.get('consumption_10')), 'EnergyConsumptionGridElectricity'))
        pair_values.append((is_str(row.get('consumption_11')), 'EnergyConsumptionTotal'))

        for value, value_type in pair_values:
            with neo.session() as session:
                device_uri = str(n[row['device_subject']])

                sensor_id = sensor_subject(config['source'], row['subject'], value_type, "RAW",
                                           freq)
                sensor_uri = str(n[sensor_id])
                measurement_id = hashlib.sha256(sensor_uri.encode("utf-8"))
                measurement_id = measurement_id.hexdigest()
                measurement_uri = str(n[measurement_id])

                create_sensor(session=session, device_uri=device_uri, sensor_uri=sensor_uri,
                              unit_uri=units["KiloW-HR"],
                              property_uri=bigg_enums[value_type],
                              estimation_method_uri=bigg_enums.Naive,
                              measurement_uri=measurement_uri, is_regular=True,
                              is_cumulative=False, is_on_change=False, freq=freq, agg_func="SUM",
                              dt_ini=pd.Timestamp(row['epc_date_before']),
                              dt_end=pd.Timestamp(row['epc_date']), ns_mappings=settings.namespace_mappings)

            data = {'listKey': measurement_id, 'isReal': False,
                    'bucket': ((pd.to_datetime(df['epc_date_before']).values.astype(
                        int) // 10 ** 9) // settings.ts_buckets) % settings.buckets,
                    'start': (pd.to_datetime(df['epc_date_before']).values.astype(int)) // 10 ** 9,
                    'end': (pd.to_datetime(df['epc_date']).values.astype(int)) // 10 ** 9, 'value': value}

            device_table = harmonized_nomenclature(mode='online', data_type=value_type, R=True, C=True,
                                                   O=True, freq=freq, user=user)

            save_to_hbase([data], device_table, hbase_conn2,
                          [("info", ['end', 'isReal']), ("v", ['value'])],
                          row_fields=['bucket', 'listKey', 'start'])

            period_table = harmonized_nomenclature(mode='batch', data_type=value_type, R=True, C=True,
                                                   O=True, freq=freq, user=user)

            save_to_hbase([data], period_table, hbase_conn2,
                          [("info", ['end', 'isReal']), ("v", ['value'])],
                          row_fields=['bucket', 'start', 'listKey'])


def harmonize_data(data, **kwargs):
    # Variables
    namespace = kwargs['namespace']
    user = kwargs['user']
    n = Namespace(namespace)
    config = kwargs['config']
    mapper = Mapper(config['source'], n)

    # Clean Data
    df = pd.DataFrame.from_records(data)
    clean_general(df, kwargs)

    # Buildings
    df_building = clean_building_info(df.copy(), config['source'])
    g = generate_rdf(mapper.get_mappings("building_info"), df_building)
    g.serialize('out.ttl', format='ttl')
    save_rdf_with_source(g, config['source'], config['neo4j'])
    link_devices_with_source(df_building, n, config['neo4j'])

    # Projects
    df_project = clean_project(df.copy())
    g = generate_rdf(mapper.get_mappings("project_info"), df_project)
    save_rdf_with_source(g, config['source'], config['neo4j'])

    # EEM & Savings
    df_eem_es = clean_eem_savings(df.copy(), config['source'])
    harmonize_eem_es(df_eem_es, mapper, config)

    # TS
    harmonize_ts(df, config, n, user)
