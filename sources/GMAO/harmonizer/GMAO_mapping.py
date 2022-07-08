import numpy as np
import pandas as pd
from rdflib import Namespace

from sources.GMAO.harmonizer.mapper import Mapper
from utils.data_transformations import decode_hbase, building_space_subject, to_object_property, maintenance_subject, \
    construction_element_subject
from utils.rdf_utils.ontology.namespaces_definition import bigg_enums
from utils.rdf_utils.rdf_functions import generate_rdf


def split_zone_name(value):
    spl = value.split('.')
    building_type = spl[0]
    building = spl[1]
    space = '.'.join(spl[1:-1])
    parent_space = '.'.join(spl[1:-2])
    return f"{building_type},{building},{space},{parent_space}"


def split_zone(value):
    spl = value.split('.')
    return '.'.join(spl[1:-1])


def harmonize_full_zone(data, **kwargs):
    df = pd.DataFrame(data)
    df = df.applymap(decode_hbase)
    df.drop(['typology', 'criticalities', 'managedscopes', 'operations', 'featuresvalues'], axis=1, inplace=True)
    df[['building_type', 'building_id', 'building_space', 'building_space_parent']] = df['zonepath'].apply(
        split_zone_name).str.split(',', expand=True)

    df['buildingSpace_subject'] = df['building_space'].apply(building_space_subject)
    df['hasSubSpace'] = df.apply(
        lambda x: building_space_subject(x['building_space_parent']) if x['building_space_parent'] != '' else np.NaN,
        axis=1)

    df['hasBuildingSpaceUseType'] = to_object_property("Public", namespace=bigg_enums)  # TODO: set taxonomy

    save_df(df, 'zones', **kwargs)


def harmonize_full_work_order(data, **kwargs):
    df = pd.json_normalize(data, sep='_')
    df = df.applymap(decode_hbase)

    df['subject'] = df['id'].apply(maintenance_subject)
    df['maintenanceActionIsPeriodic'] = False

    df[['zone_name_id', 'zone_name_name']] = df['zone_name'].str.split(' - ', expand=True)
    df['zone_name_id'] = df['zone_name_id'].str.strip()
    df['zone_name_id'] = df['zone_name_id'].apply(split_zone)

    df['isSubjectToMaintenance'] = df['zone_name_id'].apply(construction_element_subject)
    df['isAssociatedWithSpace'] = df['zone_name_id'].apply(building_space_subject)
    save_df(df, 'work_order', **kwargs)


def save_df(df, mapping_type, **kwargs):
    namespace = kwargs['namespace']
    config = kwargs['config']
    n = Namespace(namespace)

    mapper = Mapper(config['source'], n)
    g = generate_rdf(mapper.get_mappings(mapping_type), df)

    g.serialize('output.ttl', format="ttl")

    # save_rdf_with_source(g, config['source'], config['neo4j'])
