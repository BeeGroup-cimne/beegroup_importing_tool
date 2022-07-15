from functools import partial
from hashlib import sha256

import pandas as pd
from dateutil.parser import parse
from rdflib import Namespace

from sources.ePlanet.harmonizer.Mapper import Mapper
from utils.data_transformations import decode_hbase, building_subject, fuzzy_dictionary_match, fuzz_params, \
    location_info_subject, building_space_subject, building_department_subject

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

    # Organization
    df['organization_subject'] = df['Code'].apply(
        lambda x: building_department_subject(sha256(x.encode('utf-8')).hexdigest()))

    # Building
    df['building_subject'] = df['Code'].apply(lambda x: building_subject(sha256(x.encode('utf-8')).hexdigest()))
    # df['hasBuildingConstructionType'] = df['Type Of Building'].apply()
    # set_taxonomy_to_df(df, 'Name')

    # Building Space
    df['building_space_subject'] = df['Code'].apply(building_space_subject)
    # TODO: set hasBuildingSpaceUseType using taxonomy -> Label Name
    # df['hasBuildingSpaceUseType'] = df['hasBuildingSpaceUseType'].apply(building_space_subject)

    # Location
    df['location_subject'] = df['Code'].apply(lambda x: location_info_subject(sha256(x.encode('utf-8')).hexdigest()))
    df['hasLocationInfo'] = df['Code'].apply(location_info_subject)

    # fuzzy_location(Cache.province_dic, df, 'Municipality Unit', 'hasAddressProvince')
    # fuzzy_location(Cache.province_dic, df, 'Municipality Unit', 'hasAddressProvince')

    # TODO: static -> Organization, UtilityPoint, Device

    return df


def clean_ts_data(df: pd.DataFrame):
    pass


def clean_general_data(df: pd.DataFrame):
    df = df.applymap(decode_hbase)
    df['Date'] = df.apply(lambda x: parse(f"{x['Year']}/{x['Month']}/1"), axis=1)
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
