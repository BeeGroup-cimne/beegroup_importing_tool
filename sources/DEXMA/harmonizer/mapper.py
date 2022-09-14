from functools import partial

import pandas as pd
from neo4j import GraphDatabase
from rdflib import Namespace

from sources.DEXMA.harmonizer.Dexma_mapping import Mapper
from utils.data_transformations import location_info_subject, building_subject, building_space_subject, \
    gross_area_subject, device_subject
from utils.rdf_utils.rdf_functions import generate_rdf
from utils.rdf_utils.save_rdf import save_rdf_with_source
from utils.utils import log_string


def harmonize_ts(data, **kwargs): pass


def clean_location_info(data, kwargs, n):
    # LocationInfo
    df = pd.DataFrame(data)
    df = df[df['type'] == 'LEAF']

    df['location_subject'] = df['id'].apply(location_info_subject)
    df['location_uri'] = df['location_subject'].apply(lambda x: n[x])
    df['addressLatitude'] = df['address'].apply(lambda x: x['coordinates']['latitude'])
    df['addressLongitude'] = df['address'].apply(lambda x: x['coordinates']['longitude'])
    df['addressPostalCode'] = df['address'].apply(lambda x: x['zip'])

    df['addressStreetName'] = df['address'].apply(lambda x: x['street'].split(',')[0])
    df['addressStreetNumber'] = df['address'].apply(lambda x: x['street'].split(',')[-1])

    # # df['hasAddressCity'] # TODO
    # # df['hasAddressProvince'] # TODO

    # Building
    df['building_subject'] = df['key'].apply(building_subject)
    df['building_uri'] = df['building_subject'].apply(lambda x: n[x])

    # Building Space
    df['building_space_subject'] = df['key'].apply(building_space_subject)
    df['hasSpace'] = df['building_space_subject'].apply(lambda x: n[x])

    # Area
    df['area_subject'] = df['key'].apply(partial(gross_area_subject, a_source=kwargs['config']['source']))
    df['hasArea'] = df['area_subject'].apply(lambda x: n[x])

    return df


def clean_devices(data, kwargs, n):
    df = pd.json_normalize(data, sep='_')

    df['device_subject'] = df['id'].apply(partial(device_subject, source=kwargs['config']['source']))

    df_none = df[df['location_id'].isnull()]  # TODO

    df_full = df[df['location_id'].notnull()]

    for name, df_group in df_full.groupby(by=['location_id']):
        pass
        # todo: search location by id


def harmonize_static(data, **kwargs):
    namespace = kwargs['namespace']
    config = kwargs['config']
    user = kwargs['user']

    n = Namespace(namespace)

    neo4j_connection = config['neo4j']
    neo = GraphDatabase.driver(**neo4j_connection)

    mapper = Mapper(config['source'], n)
    hbase_conn = config['hbase_store_harmonized_data']

    if kwargs['collection_type'] == 'Locations':
        try:
            result = clean_location_info(data, kwargs, n)
            g = generate_rdf(mapper.get_mappings('Location'), result)
            # g.serialize('output.ttl', format="ttl")
            save_rdf_with_source(g, config['source'], config['neo4j'])
        except Exception as ex:
            log_string(f"{ex}", mongo=False)

    if kwargs['collection_type'] == 'Devices':
        try:
            result = clean_devices(data, kwargs, n)
        except Exception as ex:
            log_string(f"{ex}", mongo=False)
