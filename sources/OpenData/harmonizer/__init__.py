import pandas as pd
from neo4j import GraphDatabase
from rdflib import Namespace

from harmonizer.cache import Cache
from sources.OpenData.harmonizer.mapper import Mapper
from utils.data_transformations import location_info_subject, fuzz_location, cadastral_info_subject, \
    building_subject, additional_epc_subject, epc_subject
from utils.rdf_utils.rdf_functions import generate_rdf
from utils.rdf_utils.save_rdf import save_rdf_with_source


def clean_data(data, n, neo):
    _df = pd.DataFrame(data)

    # Building
    with neo.session() as session:
        res = session.run(
            f"""MATCH (b:bigg__Building)-[:bigg__hasCadastralInfo]-(c:bigg__CadastralInfo),
            (b:bigg__Building)<-[:bigg__managesBuilding|bigg__hasSubOrganization *]-(o:bigg__Organization{{userID:'icaen'}}) 
             RETURN b.bigg__buildingIDFromOrganization as building_id, c.bigg__landCadastralReference as cadastral_ref """).data()

    building_df = pd.DataFrame(res)

    df = pd.merge(left=building_df, right=_df, left_on='cadastral_ref',
                  right_on='referencia_cadastral')

    if not df.empty:
        # print(df.to_dict(orient='records'))

        df['building_subject'] = df['building_id'].apply(building_subject)
        df['building_uri'] = df['building_subject'].apply(lambda x: n[x])

        # Location
        df['location_subject'] = df['building_id'].apply(location_info_subject)
        df['location_uri'] = df['location_subject'].apply(lambda x: n[x])

        df['hasAddressCity'] = df['poblacio'].map(
            fuzz_location(Cache.municipality_dic_ES, ['ns1:name'], df['poblacio'].unique()))

        df['hasAddressProvince'] = df['nom_provincia'].map(
            fuzz_location(Cache.province_dic_ES, ['ns1:name', 'ns1:officialName'],
                          df['nom_provincia'].dropna().unique()))

        # Cadastral Reference
        df['cadastral_subject'] = df['referencia_cadastral'].apply(cadastral_info_subject)
        df['cadastral_uri'] = df['cadastral_subject'].apply(lambda x: n[x])

        # EPC
        df['epc_subject'] = df['num_cas'].apply(epc_subject)

        df['epc_uri'] = df['epc_subject'].apply(lambda x: n[x])

        # EPC Additional Info
        df['additional_epc_subject'] = df['num_cas'].apply(additional_epc_subject)
        df['additional_epc_uri'] = df['additional_epc_subject'].apply(lambda x: n[x])

    return df


def harmonize_data(data, **kwargs):
    namespace = kwargs['namespace']
    config = kwargs['config']
    n = Namespace(namespace)

    neo4j_connection = config['neo4j']
    neo = GraphDatabase.driver(**neo4j_connection)

    df = clean_data(data, n, neo)

    if not df.empty:
        mapper = Mapper(config['source'], n)
        g = generate_rdf(mapper.get_mappings("all"), df)

        g.serialize('output.ttl', format="ttl")

        save_rdf_with_source(g, config['source'], config['neo4j'])
