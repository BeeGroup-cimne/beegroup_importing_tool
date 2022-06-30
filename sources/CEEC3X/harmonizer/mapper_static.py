import pandas as pd
from neo4j import GraphDatabase
from rdflib import Namespace, Graph
from slugify import slugify
import ast
import settings
from harmonizer.cache import Cache
from utils.data_transformations import *
from utils.utils import log_string
from utils.rdf_utils.ontology.namespaces_definition import Bigg, bigg_enums
from utils.rdf_utils.rdf_functions import generate_rdf
from utils.rdf_utils.save_rdf import save_rdf_with_source
from .IdentificacionEdificio_mapping import Mapper as IdentificacionEdificio_Mapper
from .CondicionesFuncionamientoyOcupacion_mapping import Mapper as CondicionesFuncionamientoyOcupacion_Mapper
from .DatosGeneralesyGeometria_mapping import Mapper as DatosGeneralesyGeometria_Mapper
# get namespaces
bigg = settings.namespace_mappings['bigg']

def clean_CondicionesFuncionamientoyOcupacion_dataframes(df, sources):
    building_organization_code = df.loc[0, 'building_organization_code']
    df_spaces = pd.DataFrame.from_records(ast.literal_eval(df.loc[0, 'Espacio']))
    df_spaces.loc[:, 'building_space_main_subject'] = building_space_subject(building_organization_code)
    df_spaces.loc[:, 'building_space_current_subject'] = df_spaces.apply(lambda x:
                                                                         building_space_subject(
                                                                             f"{building_organization_code}_{x.name}"),
                                                                         axis=1)
    df_spaces.loc[:, 'building_space_current_netfloorarea_subject'] = df_spaces.apply(
        lambda x: net_area_subject(f"{building_organization_code}_{x.name}", a_source="CEEC3X"),
        axis=1)
    return df_spaces

def clean_DatosGeneralesyGeometria_dataframes(df, sources):
    df.loc[:, 'buildingspace_subject'] = df.building_organization_code.apply(building_space_subject)
    df.loc[:, 'netfloor_area_subject'] = df.building_organization_code.apply(partial(net_area_subject, a_source=sources))
    df.loc[:, 'heated_area_subject'] = df.building_organization_code.apply(partial(heated_area_subject, a_source=sources))
    df.loc[:, 'cooling_area_subject'] = df.building_organization_code.apply(partial(cooled_area_subject, a_source=sources))
    df.loc[:, 'heated_area_value'] = float(df.SuperficieHabitable) * float((float(df.PorcentajeSuperficieHabitableCalefactada)/100))
    df.loc[:, 'cooling_area_value'] = float(df.SuperficieHabitable) * float((float(df.PorcentajeSuperficieHabitableRefrigerada)/100))

def clean_IdentificacionEdificio_dataframes(df, source):
    df.loc[:, 'building_subject'] = df.building_organization_code.apply(building_subject)
    df.loc[:, 'location_subject'] = df.building_organization_code.apply(location_info_subject)
    municipality_dic = Cache.municipality_dic
    municipality_fuzz = partial(fuzzy_dictionary_match,
                                map_dict=fuzz_params(
                                    municipality_dic,
                                    ['ns1:name']
                                ),
                                default=None
                                )
    df.loc[:, 'hasAddressCity'] = df['Municipio'].apply(municipality_fuzz)
    province_dic = Cache.province_dic
    province_fuzz = partial(fuzzy_dictionary_match,
                            map_dict=fuzz_params(
                                province_dic,
                                ['ns1:name']
                            ),
                            default=None
                            )
    df.loc[:, 'hasAddressProvince'] = df['Provincia'].apply(province_fuzz)
    # hasBuildingConstructionType
    # hasAddressClimateZone
    df.loc[:, 'cadastral_subject'] = df.ReferenciaCatastral.apply(cadastral_info_subject)
    #df.loc[:, 'epc_subject'] = df.building_organization_code.apply(epc_subject()) # CANVIAR subjecte
    # EnergyPerformanceCertificate
    # EnergyPerformanceCertificateAdditionalInfo


def harmonize_IdentificacionEdificio(data, **kwargs):
    namespace = kwargs['namespace']
    user = kwargs['user']
    config = kwargs['config']
    n = Namespace(namespace)
    log_string("preparing df", mongo=False)
    df = pd.DataFrame.from_records(data)
    df = df.applymap(decode_hbase)
    clean_IdentificacionEdificio_dataframes(df, config['source'])
    mapper = IdentificacionEdificio_Mapper(config['source'], n)
    log_string("generating rdf", mongo=False)
    g = generate_rdf(mapper.get_mappings("all"), df)
    log_string("saving", mongo=False)
    save_rdf_with_source(g, config['source'], config['neo4j'])


def harmonize_DatosGeneralesyGeometria(data, **kwargs):
    namespace = kwargs['namespace']
    user = kwargs['user']
    config = kwargs['config']
    n = Namespace(namespace)
    log_string("preparing df", mongo=False)
    df = pd.DataFrame.from_records(data)
    df = df.applymap(decode_hbase)
    clean_DatosGeneralesyGeometria_dataframes(df, config['source'])
    mapper = DatosGeneralesyGeometria_Mapper(config['source'], n)
    log_string("generating rdf", mongo=False)
    g = generate_rdf(mapper.get_mappings("all"), df)
    log_string("saving", mongo=False)
    save_rdf_with_source(g, config['source'], config['neo4j'])


def harmonize_CondicionesFuncionamientoyOcupacion(data, **kwargs):
    namespace = kwargs['namespace']
    user = kwargs['user']
    config = kwargs['config']
    n = Namespace(namespace)
    log_string("preparing df", mongo=False)
    df = pd.DataFrame.from_records(data)
    df = df.applymap(decode_hbase)
    df = clean_CondicionesFuncionamientoyOcupacion_dataframes(df, config['source'])
    mapper = CondicionesFuncionamientoyOcupacion_Mapper(config['source'], n)
    log_string("generating rdf", mongo=False)
    g = generate_rdf(mapper.get_mappings("all"), df)
    log_string("saving", mongo=False)
    save_rdf_with_source(g, config['source'], config['neo4j'])

