import pandas as pd
from neo4j import GraphDatabase
from rdflib import Namespace


def harmonize_data(data, **kwargs):
    namespace = kwargs['namespace']
    user = kwargs['user']
    config = kwargs['config']

    hbase_conn2 = config['hbase_store_harmonized_data']
    neo4j_connection = config['neo4j']

    neo = GraphDatabase.driver(**neo4j_connection)
    n = Namespace(namespace)

    df = pd.DataFrame.from_records(data)

    df['Fecha inicio Docu. cálculo'] = pd.to_datetime(
        df['Fecha inicio Docu. cálculo'].dt.strftime('%Y/%m/%d 00:%M:%S'))  # ISO 8601
    df['Fecha fin Docu. cálculo'] = pd.to_datetime(
        df['Fecha fin Docu. cálculo'].dt.strftime('%Y/%m/%d 23:%M:%S'))  # ISO 8601

    df['ts_init'] = df['Fecha inicio Docu. cálculo'].astype('int') / 10 ** 9
    df['ts_init'] = df['ts_init'].astype('int')

    df['ts_end'] = df['Fecha fin Docu. cálculo'].astype('int') / 10 ** 9
    df['ts_end'] = df['ts_end'].astype('int')

    print(df)
