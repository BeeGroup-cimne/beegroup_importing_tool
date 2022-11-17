from datetime import timedelta

from rdflib import Namespace
from slugify import slugify

from sources.Bulgaria.constants import enum_energy_efficiency_measurement_type, enum_energy_saving_type
from sources.Bulgaria.harmonizer.Mapper import Mapper
from sources.Bulgaria.harmonizer.mapper_buildings import set_source_id
from sources.BulgariaDetail.utils import set_taxonomy, set_municipality
from utils.data_transformations import *
from utils.rdf_utils.rdf_functions import generate_rdf
from utils.rdf_utils.save_rdf import save_rdf_with_source, link_devices_with_source


def clean_general(df, kwargs):
    df = df.applymap(decode_hbase)
    df['building_type'] = df['building_type'].str.strip()

    df.rename(
        columns={'building_type': 'type_of_building', 'location_municipality': 'municipality',
                 'area_gross_floor_area': 'gross_floor_area'},
        inplace=True)

    set_source_id(df, kwargs['user'], kwargs['config']['neo4j'])
    set_taxonomy(df, 'municipality')
    set_municipality(df, 'municipality')

    df['subject'] = df['epc_id']

    df['epc_date'] = pd.to_datetime(df['epc_date'], infer_datetime_format=True)
    df['epc_date_before'] = df['epc_date'] - timedelta(days=365)
    df['epc_date'] = (df['epc_date'].astype('datetime64')).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    df['epc_date_before'] = (df['epc_date_before'].astype('datetime64')).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    df['epc_before_subject'] = df['subject'].apply(lambda x: x + '-before').apply(epc_subject)
    df['epc_after_subject'] = df['subject'].apply(lambda x: x + '-after').apply(epc_subject)


def clean_building_info(df, source):
    df['location_org_subject'] = df['municipality'].apply(slugify).apply(building_department_subject)
    df['organization_subject'] = df['subject'].apply(building_department_subject)
    df['building_subject'] = df['subject'].apply(building_subject)
    df['building_name'] = df.apply(lambda x: f"{x.municipality}:{x.type_of_building}", axis=1)
    df['building_id'] = df['subject']
    df['location_subject'] = df['subject'].apply(location_info_subject)

    df['building_space_subject'] = df['subject'].apply(building_space_subject)
    df['gross_floor_area_subject'] = df['subject'].apply(partial(gross_area_subject, a_source=source))
    df['element_subject'] = df['subject'].apply(construction_element_subject)
    df['device_subject'] = df['subject'].apply(partial(device_subject, source=source))
    df['utility_subject'] = df['subject'].apply(delivery_subject)
    df['project_subject'] = df['subject'].apply(project_subject)

    df['annual_energy_consumption_before_total_consumption'] = df['epc_specific_energy_consumption_before (kWh/m2)']
    df['total_savings_Investments'] = df['total_annual_savings_11']

    return df[['location_org_subject', 'municipality', 'organization_subject',
               'building_name',
               'building_subject', 'building_id', 'location_subject', 'hasAddressCity',
               'building_space_subject',
               'buildingSpaceUseType', 'gross_floor_area_subject', 'epc_before_subject', 'epc_date_before',
               'epc_energy_class_before', 'annual_energy_consumption_before_total_consumption',
               'epc_after_subject',
               'epc_date', 'epc_energy_class_after', 'project_subject', 'total_savings_Investments',
               'element_subject',
               'device_subject', 'utility_subject', 'subject'
               ]]


def clean_project(df):
    df['project_subject'] = df['subject'].apply(project_subject)

    for i, eem_type in enumerate(enum_energy_efficiency_measurement_type):
        df[f"eem_{i}_subject"] = df['subject'].apply(lambda x: f"{x}-{eem_type}").apply(eem_subject)
    for saving_type in enum_energy_saving_type:
        df[f'project_energy_saving_subject_{saving_type}'] = df['subject'] \
            .apply(lambda x: f"{x}-project-{saving_type}").apply(energy_saving_subject)
    return df[['subject', 'project_subject', 'epc_date_before', 'epc_date'] +
              [x for x in df.columns if re.match("eem_.*_subject", x)] +
              [x for x in df.columns if re.match("total_.*", x)] +
              [x for x in df.columns if re.match("energy_saving_.*_subject", x)] +
              [x for x in df.columns if re.match("project_energy_saving_subject_.*", x)]]


def harmonize_data(data, **kwargs):
    # Variables
    namespace = kwargs['namespace']
    user = kwargs['user']
    n = Namespace(namespace)
    config = kwargs['config']
    mapper = Mapper(config['source'], n)

    # Clean Data
    df = pd.DataFrame.from_records(data)
    clean_general(df, kwargs)

    # Buildings
    df_building = clean_building_info(df.copy(), config['source'])
    g = generate_rdf(mapper.get_mappings("building_info"), df_building)
    g.serialize('out.ttl', format='ttl')
    save_rdf_with_source(g, config['source'], config['neo4j'])
    link_devices_with_source(df_building, n, config['neo4j'])

    # Projects
    df_project = clean_project(df.copy())
    g = generate_rdf(mapper.get_mappings("project_info"), df_project)
    save_rdf_with_source(g, config['source'], config['neo4j'])

    # EEM & Savings

    # TS
