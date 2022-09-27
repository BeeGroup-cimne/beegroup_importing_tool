from functools import partial
from hashlib import sha256

import pandas as pd
from neo4j import GraphDatabase
from rdflib import Namespace

import settings
from harmonizer.cache import Cache
from sources.ePlanet.harmonizer.Mapper import Mapper
from utils.data_transformations import decode_hbase, building_subject, fuzzy_dictionary_match, fuzz_params, \
    location_info_subject, building_space_subject, device_subject, delivery_subject, sensor_subject
from utils.hbase import save_to_hbase
from utils.neo4j import create_sensor
from utils.nomenclature import harmonized_nomenclature, HARMONIZED_MODE
from utils.rdf_utils.ontology.namespaces_definition import units, bigg_enums
from utils.rdf_utils.rdf_functions import generate_rdf
from utils.rdf_utils.save_rdf import save_rdf_with_source

STATIC_COLUMNS = ['Year', 'Month', 'Region',
                  'Street name', 'Street number', 'Name of the building or public lighting', 'Meter number']

TS_COLUMNS = ['Year', 'Month', 'Meter number', 'Current record', 'Previous record', 'Variable', 'Recording date',
              'Previous recording date', 'StartDate', 'EndDate']


def clean_static_data(df: pd.DataFrame, **kwargs):
    namespace = kwargs['namespace']
    config = kwargs['config']
    n = Namespace(namespace)

    # # Organization
    # df['pertainsToOrganization'] = df['Code'].apply(
    #     lambda x: building_department_subject(sha256(x.encode('utf-8')).hexdigest()))

    # Building
    df['building_subject'] = df['Meter number'].apply(building_subject)

    # Building Space
    df['building_space_subject'] = df['Meter number'].apply(building_space_subject)
    df['hasSpace'] = df['building_space_subject'].apply(lambda x: n[x])

    # Location
    df['location_subject'] = df['Meter number'].apply(location_info_subject)
    df['hasLocationInfo'] = df['location_subject'].apply(lambda x: n[x])

    municipality_dic = Cache.municipality_dic_GR

    # Municipality
    municipality_fuzz = partial(fuzzy_dictionary_match,
                                map_dict=fuzz_params(municipality_dic, ['ns1:alternateName']),
                                default=None, fix_score=75)

    unique_municipality = df['Municipality'].unique()
    mun_map = {k: municipality_fuzz(k) for k in unique_municipality}
    df['hasAddressCity'] = df['Municipality'].map(mun_map)

    # Device
    df['device_subject'] = df['Meter number'].apply(partial(device_subject, source=config['source']))
    df['isObservedByDevice'] = df['device_subject'].apply(lambda x: n[x])

    # Utility Point of Delivery
    df['utility_point_subject'] = df['Meter number'].apply(delivery_subject)

    return df


def harmonize_ts_data(raw_df: pd.DataFrame, **kwargs):
    namespace = kwargs['namespace']
    config = kwargs['config']
    user = kwargs['user']

    n = Namespace(namespace)

    neo4j_connection = config['neo4j']
    neo = GraphDatabase.driver(**neo4j_connection)

    hbase_conn = config['hbase_store_harmonized_data']

    # calc
    aux_df = raw_df[raw_df['Current record'].str.isdigit()].copy()
    aux_df['aux_value'] = (aux_df['Current record'].astype(float) - aux_df['Previous record'].astype(float)) * aux_df[
        'Variable'].astype(float)
    aux_df = aux_df[aux_df['aux_value'] >= 0]

    for unique_value, df in aux_df.groupby('Meter number'):
        dt_ini = df.iloc[0]['StartDate']
        dt_end = df.iloc[-1]['EndDate']

        df['timestamp'] = df['StartDate'].view(int) // 10 ** 9

        df["ts"] = df['StartDate']
        df["bucket"] = (df['timestamp'].apply(float) // settings.ts_buckets) % settings.buckets
        df['start'] = df['timestamp'].apply(decode_hbase)
        df['end'] = df['EndDate'].view(int) // 10 ** 9
        df['value'] = df['aux_value']
        df['isReal'] = True

        df['device_subject'] = df['Meter Code'].apply(partial(device_subject, source=config['source']))

        with neo.session() as session:
            for index, row in df.iterrows():
                device_uri = str(n[row['device_subject']])
                sensor_id = sensor_subject(config['source'], row['Meter Code'],
                                           'EnergyConsumptionGridElectricity', "RAW", "")

                sensor_uri = str(n[sensor_id])
                measurement_id = sha256(sensor_uri.encode("utf-8"))
                measurement_id = measurement_id.hexdigest()
                measurement_uri = str(n[measurement_id])

                create_sensor(session, device_uri, sensor_uri, units["KiloW-HR"],
                              bigg_enums.EnergyConsumptionGridElectricity, bigg_enums.TrustedModel,
                              measurement_uri, False,
                              False, False, "", "SUM", dt_ini, dt_end, settings.namespace_mappings)

                df['listKey'] = measurement_id

                reduced_df = df[['start', 'end', 'value', 'listKey', 'bucket', 'ts', 'isReal']]

                device_table = harmonized_nomenclature(mode=HARMONIZED_MODE.ONLINE,
                                                       data_type='EnergyConsumptionGridElectricity',
                                                       R=True, C=False, O=False,
                                                       aggregation_function='SUM',
                                                       freq="", user=user)

                period_table = harmonized_nomenclature(mode=HARMONIZED_MODE.BATCH,
                                                       data_type='EnergyConsumptionGridElectricity',
                                                       R=True, C=False, O=False,
                                                       aggregation_function='SUM', freq="", user=user)

                save_to_hbase(reduced_df.to_dict(orient="records"), device_table, hbase_conn,
                              [("info", ['end', 'isReal']), ("v", ['value'])],
                              row_fields=['bucket', 'listKey', 'start'])

                save_to_hbase(df.to_dict(orient="records"), period_table, hbase_conn,
                              [("info", ['end', 'isReal']), ("v", ['value'])],
                              row_fields=['bucket', 'start', 'listKey'])


def clean_general_data(df: pd.DataFrame):
    df = df.applymap(decode_hbase)

    df['StartDate'] = df['Previous recording date'].astype(str).str.zfill(8)
    df['EndDate'] = df['Recording date'].astype(str).str.zfill(8)

    df = df[~df['StartDate'].str.contains('^0{8}$')]
    df = df[~df['EndDate'].str.contains('^0{8}$')]

    df['StartDate'] = pd.to_datetime(df['StartDate'], format="%d%m%Y")
    df['EndDate'] = pd.to_datetime(df['EndDate'], format="%d%m%Y")

    df['Meter number'] = df['Meter number'].astype(str)
    df.sort_values(by=['Meter number', 'StartDate'], inplace=True)
    df.drop_duplicates(inplace=True)
    df.columns = [s.strip() for s in df.columns]

    return df


def harmonize_data(data, **kwargs):
    namespace = kwargs['namespace']
    config = kwargs['config']
    n = Namespace(namespace)

    df = pd.DataFrame(data)
    df = clean_general_data(df)

    harmonize_static_data(config, df, kwargs, n)

    df_ts = df[TS_COLUMNS].copy()
    harmonize_ts_data(df_ts)


def harmonize_static_data(config, df, kwargs, n):
    AUX_STATIC = []
    if 'Municipality unit' in df.columns:
        AUX_STATIC.append('Municipality unit')

    if 'Municipality' in df.columns:
        AUX_STATIC.append('Municipality')

    if 'City or municipal community' in df.columns:
        AUX_STATIC.append('City or municipal community')

    df_static = df[STATIC_COLUMNS + AUX_STATIC].copy()
    df_static = clean_static_data(df_static, **kwargs)

    mapper = Mapper(config['source'], n)

    g = generate_rdf(mapper.get_mappings("static"), df_static)
    g.serialize('output.ttl', format="ttl")
    save_rdf_with_source(g, config['source'], config['neo4j'])
