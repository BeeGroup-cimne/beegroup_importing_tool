from neo4j import GraphDatabase
from pandas import pd
from rdflib import Namespace

from sources.DEXMA.harmonizer.Dexma_mapping import Mapper
from utils.data_transformations import decode_hbase, location_info_subject


def harmonize_ts(data, **kwargs): pass


def clean_location_info(data, kwargs):
    data = [{'activity': 'EDUCATION-EQUIPMENT',
             'address': {'city': 'Collbató', 'coordinates': {'latitude': 41.569294, 'longitude': 1.812986},
                         'country': {'code': 'ES', 'name': 'Spain (España)'}, 'street': 'Carrer Tarragona, 26',
                         'zip': '08293'}, 'area': 3021.74, 'area_units': 'm²', 'degree_day_method': 'UK_MET_OFFICE',
             'id': 10424, 'key': 'INA-05559', 'name': 'SES de Collbató', 'parent': {'id': 114892},
             'reference_devices': [{'device': {'id': 1173928}, 'type': 'MAINSUPPLY'},
                                   {'device': {'id': 1194967}, 'type': 'GAS'},
                                   {'device': {'id': 1194970}, 'type': 'WATER'},
                                   {'device': {'id': 1173926}, 'type': 'PHOTOVOLTAIC'}], 'summer_temp': 25.0,
             'temp_units': 'ºC', 'type': 'LEAF', 'winter_temp': 19.0}]

    # LocationInfo
    df = pd.DataFrame(data)
    df = df.applymap(decode_hbase)
    df['location_subject'] = df['key'].apply(location_info_subject)
    df['addressLatitude'] = df['address'].apply(lambda x: x['coordinates']['latitude'])
    df['addressLongitude'] = df['address'].apply(lambda x: x['coordinates']['longitude'])
    df['addressPostalCode'] = df['address'].apply(lambda x: x['zip'])
    df['addressStreetName'] = df['address'].apply(lambda x: x['street'].split(',')[0])
    df['addressStreetNumber'] = df['address'].apply(lambda x: x['street'].split(',')[1])

    # df['hasAddressCity'] # TODO
    # df['hasAddressProvince'] # TODO

    # Building

    # g = generate_rdf(mapper.get_mappings("all"), df)

    # g.serialize('output.ttl', format="ttl")


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
        clean_location_info(data, kwargs)

    if kwargs['collection_type'] == 'Devices':
        data = [{'datasource': {'id': 2410}, 'description': '', 'id': 18645, 'local_id': 'ES0113000057068634NL1P',
                 'location': None, 'name': 'ES0113000057068634NL1P', 'status': 'ACCEPTED'},
                {'datasource': {'id': 2454}, 'description': '', 'id': 18689, 'local_id': 'ES0113000057512744RE0F',
                 'location': None, 'name': 'ES0113000057512744RE0F', 'status': 'ACCEPTED'},
                {'datasource': {'id': 2440}, 'description': '', 'id': 18675, 'local_id': 'ES0122000011990507CP0F',
                 'location': None, 'name': 'ES0122000011990507CP0F', 'status': 'ACCEPTED'},
                {'datasource': {'id': 57273}, 'description': 'meteo', 'id': 1190577, 'local_id': 'meteo',
                 'location': {'id': 24905}, 'name': 'Estació Meteorològica - Aeroport BCN El Prat',
                 'status': 'ACCEPTED'},
                {'datasource': {'id': 35370}, 'description': 'meteo', 'id': 849953, 'local_id': 'meteo',
                 'location': {'id': 114887}, 'name': 'Estació meteorològica - Almoster', 'status': 'ACCEPTED'},
                {'datasource': {'id': 35381}, 'description': 'meteo', 'id': 849989, 'local_id': 'meteo',
                 'location': {'id': 114904}, 'name': 'Estació meteorològica - Almoster', 'status': 'ACCEPTED'},
                {'datasource': {'id': 32948}, 'description': 'meteo', 'id': 534050, 'local_id': 'meteo',
                 'location': {'id': 114859}, 'name': 'Estació Meteorològica - Almoster', 'status': 'ACCEPTED'},
                {'datasource': {'id': 35446}, 'description': 'meteo', 'id': 851330, 'local_id': 'meteo',
                 'location': {'id': 26039}, 'name': 'Estació Meteorològica - Almoster Abel Ferrater',
                 'status': 'ACCEPTED'},
                {'datasource': {'id': 32969}, 'description': 'meteo', 'id': 534073, 'local_id': 'meteo',
                 'location': {'id': 114871}, 'name': 'Estació Meteorològica - Amposta', 'status': 'ACCEPTED'},
                {'datasource': {'id': 35430}, 'description': 'meteo', 'id': 851311, 'local_id': 'meteo',
                 'location': {'id': 114895}, 'name': 'Estació Meteorològica - Amposta', 'status': 'ACCEPTED'}]

    # save_rdf_with_source(g, config['source'], config['neo4j'])
