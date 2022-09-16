from functools import partial

import pandas as pd
from neo4j import GraphDatabase
from rdflib import Namespace

from sources.DEXMA.harmonizer.Dexma_mapping import Mapper
from utils.data_transformations import location_info_subject, building_subject, building_space_subject, \
    gross_area_subject, device_subject, to_object_property
from utils.rdf_utils.ontology.namespaces_definition import bigg_enums
from utils.rdf_utils.rdf_functions import generate_rdf
from utils.rdf_utils.save_rdf import link_devices_with_source, save_rdf_with_source
from utils.utils import log_string


def harmonize_ts(data, **kwargs): pass


def clean_joined_devices(data, config, n):
    # LocationInfo
    df = pd.DataFrame(data)

    df['location_subject'] = df['key'].apply(location_info_subject)
    df['location_uri'] = df['location_subject'].apply(lambda x: n[x])

    df[['addressStreetName', 'addressStreetNumber']] = df['address_street'].str.split(',', expand=True)

    # df['hasAddressCity'] # TODO
    # df['hasAddressProvince'] # TODO

    # Building
    df['building_subject'] = df['key'].apply(building_subject)
    df['building_uri'] = df['building_subject'].apply(lambda x: n[x])

    # Building Space
    df['building_space_subject'] = df['key'].apply(building_space_subject)
    df['building_space_uri'] = df['building_space_subject'].apply(lambda x: n[x])

    # Area
    df['area_subject'] = df['key'].apply(partial(gross_area_subject, a_source=config['source']))
    df['hasArea'] = df['area_subject'].apply(lambda x: n[x])

    # Device
    df['device_subject'] = df['id_y'].apply(partial(device_subject, source=config['source']))
    df['hasDeviceType'] = to_object_property("Meter", namespace=bigg_enums)

    return df


def get_source_id(session, source_name):
    return session.run(f"""MATCH (n:{source_name}) RETURN id(n)""").data()[0]['id(n)']


def clean_devices_without_location(data, source):
    df = pd.DataFrame(data)
    df['device_subject'] = df['id'].apply(partial(device_subject, source=source))
    df['source_id'] = source

    return df


def harmonize_static(data, **kwargs):
    # import utils
    # config = utils.utils.read_config('config.json')
    # namespace = "https://infraestructures.cat#"
    # user = "icat"

    namespace = kwargs['namespace']
    config = kwargs['config']

    neo4j_connection = config['neo4j']
    neo = GraphDatabase.driver(**neo4j_connection)

    n = Namespace(namespace)

    if kwargs['collection_type'] == 'Devices-None':
        try:
            with neo.session() as session:
                source_id = get_source_id(session, f"{config['source']}Source")  # TODO: Change

            df = clean_devices_without_location(data, source_id)
            link_devices_with_source(df, n, config['neo4j'])
        except Exception as ex:
            log_string(f"{ex}", mongo=False)

    if kwargs['collection_type'] == 'Devices-Joined':
        try:
            mapper = Mapper(config['source'], n)

            df = clean_joined_devices(data, config, n)
            g = generate_rdf(mapper.get_mappings("Devices-Joined"), df)
            g.serialize('output.ttl', format="ttl")
            save_rdf_with_source(g, config['source'], config['neo4j'])

        except Exception as ex:
            log_string(f"{ex}", mongo=False)
