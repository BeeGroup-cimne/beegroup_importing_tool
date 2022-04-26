from neo4j import GraphDatabase
from rdflib import Namespace
import pandas as pd


def harmonize_command_line():
    pass


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
    n = Namespace(namespace)

    # Database connections

    neo4j_connection = config['neo4j']
    neo = GraphDatabase.driver(**neo4j_connection)

    # BuildingName =  filename+id+municipality+type
    # EnergyEfficiencyMeasurement
    # Location
    # EnergySavings

    with neo.session() as session:

        # Organization
        organization_name = "BulgariaOrganization"
        source_name = "BulgariaSource"

        # organization_query = f"""MERGE (s:bigg__Organization{{bigg__organizationDivisionType:"Building",bigg__organizationName:"{organization_name}"}}) RETURN s"""
        # source_query = f"""MERGE (so:{source_name})"""
        # query_relation_hasSource = f"""MATCH (o:bigg__Organization{{bigg__organizationName:"{organization_name}"}}),(s:{source_name}) CREATE (o)-[r:bigg__hasSource]->(s) RETURN o,s"""

        organization_id = session.run(
            f"""MATCH (o:bigg__Organization{{bigg__organizationDivisionType:"Building",bigg__organizationName:"{organization_name}"}})-[:bigg__hasSource]->(s:{source_name}) return id(o)""").single()

        # Building
        building_uri = n[f""]
        for i in df.to_dict(orient="records")[:1]:
            building_id = f"{i['filename']}~{i['id']}"
            building_name = f"{i['filename']}-{i['id']}- {i['municipality']}-{i['type_of_building']}"
            building_query = f"""MERGE (b:bigg__Building{{bigg__buildingIDFromOrganization:"{building_id}",
            bigg__buildingConstructionType:"{i['type_of_building']}",
            bigg__buildingName:"{building_name}"
            }}) RETURN id(b)"""

            id = 36661

            relation_query = f"""MATCH (o:bigg__Organization{{bigg__organizationName:"{organization_name}"}}), (b) WHERE id(b)={id}  MERGE (b)-[r:bigg_managesBuilding]->(o) return b"""

            print(i)
            building_space_uri = n[f"{i['filename']}~{i['id']}"]
            bulding_space_query = f"""MERGE (bs:bigg__BuildingSpace{{bigg__buildingSpaceName:"Building",uri:"{building_space_uri}"}}) RETURN bs"""
