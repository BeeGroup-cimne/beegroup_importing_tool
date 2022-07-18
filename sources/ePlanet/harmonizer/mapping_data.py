from functools import partial
from hashlib import sha256

import numpy as np
import pandas as pd
from dateutil.parser import parse
from neo4j import GraphDatabase
from rdflib import Namespace

import settings
from sources.ePlanet.harmonizer.Mapper import Mapper
from utils.data_transformations import decode_hbase, building_subject, fuzzy_dictionary_match, fuzz_params, \
    location_info_subject, building_space_subject, device_subject, delivery_subject, sensor_subject
from utils.neo4j import create_sensor
from utils.rdf_utils.ontology.namespaces_definition import units, bigg_enums

STATIC_COLUMNS = ['Year', 'Month', 'Code', 'Municipality Unit', 'Municipality', 'Region',
                  'Office', 'Meter num', 'Bill num', 'Bill num 2', 'Name', 'Street',
                  'Street num', 'City', 'Meter Code', 'Type Of Building', 'Account Type',
                  'Municipality Unit 1']

TS_COLUMNS = ['Year', 'Month', 'Code', 'Bill num', 'Bill num 2', 'Bill Issuing Day',
              'Meter Code', 'Current Record', 'Previous Record',
              'Variable', 'Recording Date', 'Previous Recording Date',
              'Electricity Consumption', 'Electricity Cost', 'VAT', 'Other',
              'Prev payment', 'Energy Value', 'VAT Prev Payment', 'EPT',
              'Out service', 'Debit/Credit', 'ETMEAR', 'VAT ETMEAR', 'Special TAX',
              'TAX', 'Low VAT', 'High VAT', 'Intermediate Value',
              'Total Energy Value', 'Total VAT of electricity', 'Total VAT Services',
              'Total VAT', 'Total ERT', 'Municipal TAX', 'Total TAP', 'EETIDE',
              'Total Account', 'Total Current Month', 'Account Type',
              'Municipality Unit 1']


def clean_static_data(df: pd.DataFrame, **kwargs):
    namespace = kwargs['namespace']
    config = kwargs['config']
    n = Namespace(namespace)

    # # Organization
    # df['pertainsToOrganization'] = df['Code'].apply(
    #     lambda x: building_department_subject(sha256(x.encode('utf-8')).hexdigest()))

    # Building
    df['building_subject'] = df['Meter Code'].apply(building_subject)
    # df['hasBuildingConstructionType'] = df['Type Of Building'].apply()
    # set_taxonomy_to_df(df, 'Name')

    # Building Space
    df['building_space_subject'] = df['Meter Code'].apply(building_space_subject)
    df['hasSpace'] = df['building_space_subject'].apply(lambda x: n[x])
    # TODO: set hasBuildingSpaceUseType using taxonomy -> Label Name
    # df['hasBuildingSpaceUseType'] = df['hasBuildingSpaceUseType'].apply(building_space_subject)

    # Location
    df['location_subject'] = df['Meter Code'].apply(location_info_subject)
    df['hasLocationInfo'] = df['location_subject'].apply(lambda x: n[x])
    # fuzzy_location(Cache.province_dic, df, 'Municipality Unit', 'hasAddressProvince')
    # fuzzy_location(Cache.municipality_dic, df, 'Municipality', 'hasAddressCity')

    # Device
    df['device_subject'] = df['Meter Code'].apply(partial(device_subject, source=config['source']))
    df['isObservedByDevice'] = df['device_subject'].apply(lambda x: n[x])

    # Utility Point of Delivery
    df['utility_point_subject'] = df['Meter Code'].apply(delivery_subject)

    return df


def clean_ts_data(raw_df: pd.DataFrame, **kwargs):
    namespace = kwargs['namespace']
    config = kwargs['config']
    user = kwargs['user']
    freq = 'None'

    n = Namespace(namespace)

    df_group = raw_df.groupby('Meter Code')
    neo4j_connection = config['neo4j']
    neo = GraphDatabase.driver(**neo4j_connection)

    hbase_conn = config['hbase_store_harmonized_data']

    for unique_value, df in df_group:
        df['timestamp'] = df['Date'].view(int) // 10 ** 9
        df['EndDate'] = df['Date'].shift(-1)

        df["ts"] = df['Date']
        df["bucket"] = (df['timestamp'].apply(float) // settings.ts_buckets) % settings.buckets
        df['start'] = df['timestamp'].apply(decode_hbase)
        df['end'] = df['EndDate'].view(int) / 10 ** 9
        df['value'] = df['value']
        df['isReal'] = True

        df['device_subject'] = df['Meter Code'].apply(partial(device_subject, source=config['source']))

    with neo.session() as session:
        for index, row in df.iterrows():
            device_uri = str(n[row['device_subject']])
            sensor_id = sensor_subject(config['source'], row['subject'], 'EnergyConsumptionGridElectricity', "RAW",
                                       freq)

            sensor_uri = str(n[sensor_id])
            measurement_id = sha256(sensor_uri.encode("utf-8"))
            measurement_id = measurement_id.hexdigest()
            measurement_uri = str(n[measurement_id])
            create_sensor(session, device_uri, sensor_uri, units["KiloW-HR"],
                          bigg_enums.EnergyConsumptionGridElectricity, bigg_enums.TrustedModel,
                          measurement_uri,
                          False, False, freq, "SUM", row['Date'], row['epc_date'])

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


def clean_general_data(df: pd.DataFrame):
    df = df.applymap(decode_hbase)
    df['Date'] = df.apply(lambda x: parse(f"{x['Year']}/{x['Month']}/1"), axis=1)
    df['Meter Code'] = df['Meter Code'].astype(str)
    df.sort_values(by=['Meter Code', 'Date'], inplace=True)

    return df


def fuzzy_location(location_cache, df, df_label, relation):
    fuzz = partial(fuzzy_dictionary_match,
                   map_dict=fuzz_params(
                       location_cache,
                       ['ns1:name']
                   ),
                   default=None
                   )

    unique_province = df[df_label].unique()
    province_map = {k: fuzz(k) for k in unique_province}
    df.loc[:, relation] = df[df_label].map(province_map)


def harmonize_data(data, **kwargs):
    namespace = kwargs['namespace']
    config = kwargs['config']
    n = Namespace(namespace)

    df = pd.DataFrame(data)
    df = clean_general_data(df)

    df_static = df[STATIC_COLUMNS].copy()
    df_ts = df[TS_COLUMNS].copy()

    clean_static_data(df_static, **kwargs)
    clean_ts_data(df_ts)

    mapper = Mapper(config['source'], n)
    # g = generate_rdf(mapper.get_mappings("all"), df)
    #
    # g.serialize('output.ttl', format="ttl")
    #
    # save_rdf_with_source(g, config['source'], config['neo4j'])
