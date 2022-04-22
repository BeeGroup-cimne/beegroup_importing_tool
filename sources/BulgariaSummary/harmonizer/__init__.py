from neo4j import GraphDatabase
from rdflib import Namespace
import pandas as pd


def harmonize_data(data, **kwargs):
    df = pd.DataFrame().from_records(data)
    df['type_of_building'] = df['type_of_building'].str.strip()

    # Match Taxonomy

    tax_df = pd.read_excel("data/tax/TAX_BULGARIA.xlsx", header=None, names=["Source", "Taxonomy"], sheet_name='Hoja1')

    tax_dict = {}
    for i in tax_df.to_dict(orient="records"):
        tax_dict.update({i['Source']: i['Taxonomy']})

    df['type_of_building'] = df['type_of_building'].map(tax_dict)

    # Variables
    namespace = kwargs['namespace']
    user = kwargs['user']
    config = kwargs['config']

    # Database connections

    neo4j_connection = config['neo4j']
    neo = GraphDatabase.driver(**neo4j_connection)

    # BuildingName =  filename+id+municipality+type
    # EnergyEfficiencyMeasurement
    # Location
    # EnergySavings

    with neo.session() as session:
        n = Namespace(namespace)
        bulding_uri = n[f""]
