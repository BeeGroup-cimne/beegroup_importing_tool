import pandas as pd
from rdflib import Namespace

from utils.data_transformations import building_subject, decode_hbase
from utils.rdf_utils.rdf_functions import generate_rdf


def harmonize_building_info(data, **kwargs):
    namespace = kwargs['namespace']
    user = kwargs['user']
    n = Namespace(namespace)
    config = kwargs['config']

    df = pd.DataFrame(data,
                      columns=['Unique ID', 'Country', 'Region', 'Municipality', 'Road', 'Road Number', 'PostalCode',
                               'Longitude',
                               'Latitude', 'Name', 'Use Type', 'Owner', 'YearOfConstruction', 'GrossFloorArea',
                               'Occupancy hours', 'Number of users', 'Renewable',
                               'EnergyAudit', 'Monitoring', 'SolarPV', 'SolarPVPower', 'SolarThermal',
                               'SolarThermalPower', 'EnergyCertificate',
                               'EnergyCertificateDate', '-', 'EnergyCertificateQualification', 'HeatingSource',
                               'OriginalInstalledPower', 'NominalPower', 'DHW source', 'OriginalInstalledPowerAfter',
                               'CoolingSource', 'CoolingPower'])

    df = df.apply(decode_hbase)
    df['building_subject'] = df['Unique ID'].apply(building_subject)
    mapper = Mapper(config['source'], n)
    g = generate_rdf(mapper.get_mappings("project_info"), df)
    # save_rdf_with_source(g, config['source'], config['neo4j'])

def harmonize_building_emm(data, **kwargs):
    namespace = kwargs['namespace']
    user = kwargs['user']
    n = Namespace(namespace)
    config = kwargs['config']
    print(data)


def harmonize_municipality_ts(data, **kwargs):
    namespace = kwargs['namespace']
    user = kwargs['user']
    n = Namespace(namespace)
    config = kwargs['config']


def harmonize_region_ts(data, **kwargs):
    namespace = kwargs['namespace']
    user = kwargs['user']
    n = Namespace(namespace)
    config = kwargs['config']
    print(data)
