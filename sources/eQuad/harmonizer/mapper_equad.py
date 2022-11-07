import pandas as pd
from neo4j import GraphDatabase
from rdflib import Namespace

from utils.data_transformations import project_subject, fuzz_data, load_dic


def clean_data(data):
    df = pd.DataFrame(data)

    # Project
    df['project_subject'] = df['_id'].apply(project_subject)

    df['currencyCode'] = list(df['projectCurrency'].apply(lambda x: x['currencyCode']))
    unique_code = list(df['currencyCode'].unique())
    currency_map = fuzz_data(load_dic(["utils/rdf_utils/ontology/dictionaries/units.ttl"]), ['qudt:expression'],
                             unique_code)
    df['hasProjectInvestmentCurrency'] = df['currencyCode'].map(currency_map)

    return df


def harmonize_data(data, **kwargs):
    namespace = kwargs['namespace']
    config = kwargs['config']
    n = Namespace(namespace)

    neo4j_connection = config['neo4j']
    neo = GraphDatabase.driver(**neo4j_connection)

    df = clean_data(data, n, neo)

    # if not df.empty:
    #     mapper = Mapper(config['source'], n)
    #     g = generate_rdf(mapper.get_mappings("all"), df)
    #
    #     g.serialize('output.ttl', format="ttl")
    #
    #     save_rdf_with_source(g, config['source'], config['neo4j'])
