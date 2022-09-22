from functools import partial
from hashlib import md5

import pandas as pd
from rdflib import Namespace

from harmonizer.cache import Cache
from sources.OpenData.harmonizer.mapper import Mapper
from utils.data_transformations import location_info_subject, fuzz_location, cadastral_info_subject, building_subject, \
    building_space_subject, get_taxonomy_mapping, to_object_property, epc_subject, project_subject
from utils.rdf_utils.ontology.namespaces_definition import bigg_enums
from utils.rdf_utils.rdf_functions import generate_rdf
from utils.rdf_utils.save_rdf import save_rdf_with_source


def clean_data(data, n):
    df = pd.DataFrame(data)

    # Location
    df['location_subject'] = df['num_cas'].apply(location_info_subject)
    df['location_uri'] = df['location_subject'].apply(lambda x: n[x])

    df['hasAddressCity'] = df['poblacio'].map(
        fuzz_location(Cache.municipality_dic_ES, ['ns1:name'], df['poblacio'].unique()))

    df['hasAddressProvince'] = df['nom_provincia'].map(
        fuzz_location(Cache.province_dic_ES, ['ns1:name', 'ns1:officialName'], df['nom_provincia'].dropna().unique()))

    # Cadastral Reference
    df['cadastral_subject'] = df['num_cas'].apply(cadastral_info_subject)
    df['cadastral_uri'] = df['cadastral_subject'].apply(lambda x: n[x])

    # Building
    df['unique_value'] = df.apply(
        lambda x: md5(f"{x['codi_postal']}-{x['adre_a']}-{x['numero']}".encode("utf-8")).hexdigest(), axis=1)

    df['building_subject'] = df['unique_value'].apply(building_subject)
    df['building_uri'] = df['building_subject'].apply(lambda x: n[x])

    # Building Space
    df['building_space_subject'] = df['unique_value'].apply(building_space_subject)

    df['hasBuildingSpaceUseType'] = df['us_edifici'].map(
        get_taxonomy_mapping('sources/OpenData/harmonizer/tax.xlsx', default='Other',
                             sheet_name="hasBuildingSpaceUseType")).apply(
        partial(to_object_property, namespace=bigg_enums))

    # EPC
    df['epc_subject'] = df['num_cas'].apply(epc_subject)

    # Project
    df['project_subject'] = df['num_cas'].apply(project_subject)
    df['hasProjectMotivation'] = df['motiu_de_la_certificacio'].map(
        get_taxonomy_mapping('sources/OpenData/harmonizer/tax.xlsx', default='Other',
                             sheet_name='hasProjectMotivation')).apply(
        partial(to_object_property, namespace=bigg_enums))

    # qualificacio_d_emissions , emissions_de_co2

    return df


def harmonize_data(data, **kwargs):
    namespace = kwargs['namespace']
    config = kwargs['config']
    n = Namespace(namespace)
    df = clean_data(data, n)

    mapper = Mapper(config['source'], n)
    g = generate_rdf(mapper.get_mappings("all"), df)

    g.serialize('output.ttl', format="ttl")

    save_rdf_with_source(g, config['source'], config['neo4j'])
