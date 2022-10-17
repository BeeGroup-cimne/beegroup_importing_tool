import pandas as pd
from neo4j import GraphDatabase
from rdflib import Namespace


def clean_data(data):
    df = pd.json_normalize(data, sep='_')

    # Building


def harmonize_data(data, **kwargs):
    namespace = kwargs['namespace']
    config = kwargs['config']
    n = Namespace(namespace)

    neo4j_connection = config['neo4j']
    neo = GraphDatabase.driver(**neo4j_connection)

    # df = clean_data(data, n, neo)
    #
    # if not df.empty:
    #     mapper = Mapper(config['source'], n)
    #     g = generate_rdf(mapper.get_mappings("all"), df)
    #
    #     g.serialize('output.ttl', format="ttl")
    #
    #     save_rdf_with_source(g, config['source'], config['neo4j'])
