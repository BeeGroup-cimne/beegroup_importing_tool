from neo4j import GraphDatabase
from rdflib import Namespace


def harmonize_general_info(data, **kwargs):
    namespace = kwargs['namespace']
    user = kwargs['user']
    config = kwargs['config']

    neo = GraphDatabase.driver(**config['neo4j'])
    n = Namespace(namespace)

    # Building, Location, Cadastral Reference, Area, Organization, EnergyPerformanceCertificate
    data = data[0]

    with neo.session() as session:
        location_uri = n[f"-LOCATION-{data['epc_id']}"]
        town = data['location_town'].replace('\"', "")
        location_query = f"""
                MERGE (d:ns0__LocationInfo{{
                         ns0__addressCity:"{town}",
                         ns0__addressProvince:"{data['location_municipality']}",
                         ns0__addressClimateZone:"{data['climate_zone']}",
                         uri:"{location_uri}"
                         }}) 
                         RETURN d"""
        print(location_query)

        cadastral_uri = n[f"{data['cadastral_reference']}"]
        cadastral_query = f"""
                MERGE (d:ns0__LocationInfo{{
                         ns0__landCadastralReference:"{data['cadastral_reference']}",
                         uri:"{cadastral_uri}",
                         }}) 
                         RETURN d"""


def harmonize_consumption_info(data, **kwargs):
    pass


def harmonize_distribution_info(data, **kwargs):
    pass


def harmonize_energy_saved(data, **kwargs):
    # EnergySavings
    pass


def harmonize_total_annual_savings(data, **kwargs):
    # Measurements
    pass


def harmonize_measurements(data, **kwargs):
    # Measurements
    pass
