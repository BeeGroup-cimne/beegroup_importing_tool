from functools import partial

import pandas as pd
from neo4j import GraphDatabase
from rdflib import Namespace

from sources.DEXMA.harmonizer.Dexma_mapping import Mapper
from utils.data_transformations import location_info_subject, building_subject, building_space_subject, \
    gross_area_subject, device_subject
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


def clean_devices(data, kwargs, n, neo):
    data = [{'datasource': {'id': 11060}, 'description': 'ID:115241', 'id': 111077, 'local_id': '115241',
             'location': {'id': 24067}, 'name': 'xxx Temp ext', 'status': 'ACCEPTED'},
            {'datasource': {'id': 11060}, 'description': 'ID:96076', 'id': 111078, 'local_id': '96076',
             'location': None, 'name': 'xxx Temp imp cf', 'status': 'ACCEPTED'},
            {'datasource': {'id': 8471}, 'description': 'device 90032', 'id': 67905, 'local_id': '90032',
             'location': {'id': 184391}, 'name': 'xxx Temp int', 'status': 'ACCEPTED'},
            {'datasource': {'id': 11060}, 'description': 'ID:115215', 'id': 90131, 'local_id': '115215',
             'location': {'id': 24067}, 'name': 'xxx Temp int', 'status': 'ACCEPTED'},
            {'datasource': {'id': 54263}, 'description': ' ', 'id': 1147347, 'local_id': '3d',
             'location': {'id': 25220}, 'name': 'Temp Solar', 'status': 'ACCEPTED'},
            {'datasource': {'id': 54252}, 'description': ' ', 'id': 1147568, 'local_id': '6d',
             'location': {'id': 25221}, 'name': 'Temp Solar', 'status': 'ACCEPTED'},
            {'datasource': {'id': 649}, 'description': 'test total', 'id': 7770, 'local_id': 'G_7',
             'location': None, 'name': 'Total', 'status': 'ACCEPTED'},
            {'datasource': {'id': 57153}, 'description': 'meteo', 'id': 1181561, 'local_id': 'meteo',
             'location': {'id': 239492}, 'name': 'Vila-Rodona Estació Meteorològica', 'status': 'ACCEPTED'},
            {'datasource': {'id': 57158}, 'description': 'meteo', 'id': 1181568, 'local_id': 'meteo',
             'location': {'id': 239495}, 'name': 'Vila-Rodona Estació Meteorològica', 'status': 'ACCEPTED'},
            {'datasource': {'id': 57154}, 'description': 'meteo', 'id': 1181562, 'local_id': 'meteo',
             'location': {'id': 239496}, 'name': 'Vila-Seca Estació Meteorològica', 'status': 'ACCEPTED'},
            {'datasource': {'id': 34034}, 'description': '', 'id': 820477, 'local_id': 'W1', 'location': None,
             'name': 'W1', 'status': 'ACCEPTED'},
            {'datasource': {'id': 11060}, 'description': 'GENERAL TOROIDALES', 'id': 89925, 'local_id': '1',
             'location': None, 'name': 'xxx ARGeneral', 'status': 'ACCEPTED'},
            {'datasource': {'id': 11060}, 'description': ' ', 'id': 113397, 'local_id': 'DD-24067',
             'location': {'id': 24067}, 'name': 'xxx DD CEIP CAN GAMBÚS', 'status': 'ACCEPTED'},
            {'datasource': {'id': 8471}, 'description': ' device 84147', 'id': 67903, 'local_id': '84147',
             'location': {'id': 184391}, 'name': 'xxx Temp ext', 'status': 'ACCEPTED'}]

    df = pd.json_normalize(data, sep='_')

    df['device_subject'] = df['id'].apply(partial(device_subject, source=kwargs['config']['source']))

    df_none = df[df['location_id'].isnull()].copy()  # TODO

    df_full = df[df['location_id'].notnull()].copy()
    df_full['location_id'] = df_full['location_id'].astype(int)

    for name, df_group in df_full.groupby(by=['location_id']):
        location_uri = n[location_info_subject(name)]

        with neo.session() as session:
            building = session.run(
                f"""MATCH (n:bigg__LocationInfo)-[r:bigg__hasLocationInfo]-(b:bigg__Building) 
                    WHERE n.uri starts with '{location_uri}' 
                    RETURN b""").data()[0]['b']

        print(building['uri'])


def harmonize_static(data, **kwargs):
    namespace = kwargs['namespace']
    config = kwargs['config']
    user = kwargs['user']

    neo4j_connection = config['neo4j']
    neo = GraphDatabase.driver(**neo4j_connection)

    hbase_conn = config['hbase_store_harmonized_data']

    n = Namespace(namespace)
    mapper = Mapper(config['source'], n)

    if kwargs['collection_type'] == 'Devices-None':
        try:
            pass
            # result = clean_devices
            # g = generate_rdf(mapper.get_mappings('Location'), result)
            # # g.serialize('output.ttl', format="ttl")
            # save_rdf_with_source(g, config['source'], config['neo4j'])
        except Exception as ex:
            log_string(f"{ex}", mongo=False)

    if kwargs['collection_type'] == 'Devices-Joined':
        try:
            df = pd.DataFrame(data)
        except Exception as ex:
            log_string(f"{ex}", mongo=False)
