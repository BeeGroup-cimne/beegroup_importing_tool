from functools import partial

import pandas as pd
from neo4j import GraphDatabase
from rdflib import Namespace

from sources.DEXMA.harmonizer.Dexma_mapping import Mapper
from utils.data_transformations import location_info_subject, building_subject, building_space_subject, \
    gross_area_subject
from utils.rdf_utils.rdf_functions import generate_rdf


def harmonize_ts(data, **kwargs): pass


def clean_location_info(data, kwargs, n):
    data = [{'activity': 'EDUCATION-EQUIPMENT',
             'address': {'city': 'Blanes', 'coordinates': {'latitude': 41.674534, 'longitude': 2.781196},
                         'country': {'code': 'ES', 'name': 'Spain (España)'}, 'street': 'Carrer Rubén Darío, 12',
                         'zip': '17300'}, 'area': 3410.0, 'area_units': 'm²', 'degree_day_method': 'UK_MET_OFFICE',
             'id': 25653, 'key': 'PNG-02443', 'name': 'CEIP Pinya de Rosa (Can Borrell)', 'parent': {'id': 114863},
             'reference_devices': [{'device': {'id': 1043035}, 'type': 'MAINSUPPLY'},
                                   {'device': {'id': 1042834}, 'type': 'GAS'},
                                   {'device': {'id': 1042829}, 'type': 'INDOORTEMP'},
                                   {'device': {'id': 1042832}, 'type': 'OUTDOORTEMP'},
                                   {'device': {'id': 534056}, 'type': 'EXTERNAL_RELATIVE_HUMIDITY'}],
             'summer_temp': 25.0, 'temp_units': 'ºC', 'type': 'LEAF', 'winter_temp': 19.0}]

    # LocationInfo
    df = pd.DataFrame(data)
    # df = df.applymap(decode_hbase)

    df['location_subject'] = df['key'].apply(location_info_subject)
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


def harmonize_static(data, **kwargs):
    namespace = kwargs['namespace']
    config = kwargs['config']
    user = kwargs['user']

    n = Namespace(namespace)

    neo4j_connection = config['neo4j']
    neo = GraphDatabase.driver(**neo4j_connection)

    mapper = Mapper(config['source'], n)
    hbase_conn = config['hbase_store_harmonized_data']

    if kwargs['collection_type'] == 'Location':
        result = clean_location_info(data, kwargs, n)
        g = generate_rdf(mapper.get_mappings('Location'), result)
        g.serialize('output.ttl', format="ttl")

    # if kwargs['collection_type'] == 'Devices':
    #     data = [{'datasource': {'id': 2410}, 'description': '', 'id': 18645, 'local_id': 'ES0113000057068634NL1P',
    #              'location': None, 'name': 'ES0113000057068634NL1P', 'status': 'ACCEPTED'},
    #             {'datasource': {'id': 2454}, 'description': '', 'id': 18689, 'local_id': 'ES0113000057512744RE0F',
    #              'location': None, 'name': 'ES0113000057512744RE0F', 'status': 'ACCEPTED'},
    #             {'datasource': {'id': 2440}, 'description': '', 'id': 18675, 'local_id': 'ES0122000011990507CP0F',
    #              'location': None, 'name': 'ES0122000011990507CP0F', 'status': 'ACCEPTED'},
    #             {'datasource': {'id': 57273}, 'description': 'meteo', 'id': 1190577, 'local_id': 'meteo',
    #              'location': {'id': 24905}, 'name': 'Estació Meteorològica - Aeroport BCN El Prat',
    #              'status': 'ACCEPTED'},
    #             {'datasource': {'id': 35370}, 'description': 'meteo', 'id': 849953, 'local_id': 'meteo',
    #              'location': {'id': 114887}, 'name': 'Estació meteorològica - Almoster', 'status': 'ACCEPTED'},
    #             {'datasource': {'id': 35381}, 'description': 'meteo', 'id': 849989, 'local_id': 'meteo',
    #              'location': {'id': 114904}, 'name': 'Estació meteorològica - Almoster', 'status': 'ACCEPTED'},
    #             {'datasource': {'id': 32948}, 'description': 'meteo', 'id': 534050, 'local_id': 'meteo',
    #              'location': {'id': 114859}, 'name': 'Estació Meteorològica - Almoster', 'status': 'ACCEPTED'},
    #             {'datasource': {'id': 35446}, 'description': 'meteo', 'id': 851330, 'local_id': 'meteo',
    #              'location': {'id': 26039}, 'name': 'Estació Meteorològica - Almoster Abel Ferrater',
    #              'status': 'ACCEPTED'},
    #             {'datasource': {'id': 32969}, 'description': 'meteo', 'id': 534073, 'local_id': 'meteo',
    #              'location': {'id': 114871}, 'name': 'Estació Meteorològica - Amposta', 'status': 'ACCEPTED'},
    #             {'datasource': {'id': 35430}, 'description': 'meteo', 'id': 851311, 'local_id': 'meteo',
    #              'location': {'id': 114895}, 'name': 'Estació Meteorològica - Amposta', 'status': 'ACCEPTED'}]

    # save_rdf_with_source(g, config['source'], config['neo4j'])
