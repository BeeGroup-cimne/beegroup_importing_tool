from neo4j import GraphDatabase
from rdflib import Namespace, Graph
from slugify import slugify

import settings
from utils.data_transformations import *
from utils.utils import log_string
from utils.rdf_utils.ontology.namespaces_definition import Bigg, bigg_enums
from utils.rdf_utils.rdf_functions import generate_rdf
from utils.rdf_utils.save_rdf import save_rdf_with_source
from .BIS_mapping import Mapper
from .transform_functions import *

# get namespaces
bigg = settings.namespace_mappings['bigg']


def clean_dataframe(df):
    df['department_organization'] = df["Departments"].apply(lambda x: ";".join([slugify(x1) for x1 in x.split(";")]))
    df['building_organization'] = df['Unique Code'].apply(lambda x: x.replace("-", "_")).apply(building_department_subject)
    df['building'] = df['Unique Code'].apply(lambda x: x.replace("-", "_")).apply(building_subject)
    df['location_info'] = df['Unique Code'].apply(lambda x: x.replace("-", "_")).apply(location_info_subject)
    country_dic = load_dic(["utils/rdf_utils/ontology/dictionaries/countries.ttl"])
    country_fuzz = partial(fuzzy_dictionary_match,
                            map_dict=fuzz_params(country_dic, ['ns1:countryCode']),
                            default=None
                            )
    unique_country = df['Country'].unique()
    country_map = {k: country_fuzz(k) for k in unique_country}
    df['hasAddressCountry'] =df['Country'].map(country_map)

    province_dic = load_dic(["utils/rdf_utils/ontology/dictionaries/province.ttl"])
    municipality_dic = load_dic(["utils/rdf_utils/ontology/dictionaries/municipality.ttl"])

    for country, country_uri in country_map.items():
        if country_uri is not None:
            province_fuzz = partial(fuzzy_dictionary_match,
                                   map_dict=fuzz_params(
                                       province_dic,
                                       ['ns1:name'],
                                        filter_query=f"SELECT ?s ?p ?o WHERE{{?s ?p ?o . ?s ns1:parentCountry <{country_uri}>}}"
                                   ),
                                   default=None
                                   )
        else:
            province_fuzz = partial(fuzzy_dictionary_match,
                                    map_dict=fuzz_params(
                                        province_dic,
                                        ['ns1:name']
                                    ),
                                    default=None
                                    )
        df_group = df.groupby('Country').get_group(country)
        unique_prov = df_group['Administration Level 2'].unique()
        prov_map = {k: province_fuzz(k) for k in unique_prov}
        df.loc[df['Country']==country, 'hasAddressProvince'] = df['Administration Level 2'].map(prov_map)

        for prov, prov_uri in prov_map.items():
            if prov_uri is not None:
                municipality_fuzz = partial(fuzzy_dictionary_match,
                                        map_dict=fuzz_params(
                                            municipality_dic,
                                            ['ns1:name'],
                                            filter_query=f"SELECT ?s ?p ?o WHERE{{?s ?p ?o . ?s ns1:parentADM2 <{country_uri}>}}"
                                        ),
                                        default=None
                                        )
            else:
                municipality_fuzz = partial(fuzzy_dictionary_match,
                                        map_dict=fuzz_params(
                                            municipality_dic,
                                            ['ns1:name']
                                        ),
                                        default=None
                                        )
            df_i_group = df_group.groupby('Administration Level 2').get_group(prov)
            unique_city = df_i_group['Administration Level 3'].unique()
            city_map = {k: municipality_fuzz(k) for k in unique_city}
            df.loc[df['Administration Level 2']==prov, 'hasAddressCity'] = df_group['Administration Level 3'].map(city_map)
    df['Cadastral References'] = df['Cadastral References'].apply(validate_ref_cadastral)

    df['building_space'] = df['Unique Code'].apply(lambda x: x.replace("-", "_")).apply(building_space_subject)

    building_type_taxonomy = get_taxonomy_mapping(
        taxonomy_file="sources/BIS/harmonizer/BuildingUseTypeTaxonomyInfraestructures.xls",
        default="Other")

    df['hasBuildingSpaceUseType'] = df['Use Type'].map(building_type_taxonomy). \
        apply(partial(to_object_property, namespace=bigg_enums))

    df['gross_floor_area'] = df['Unique Code'].apply(lambda x: x.replace("-", "_")).\
        apply(partial(gross_area_subject, a_source="GPGSource"))
    df['gross_floor_area_above_ground'] = df['Unique Code'].apply(lambda x: x.replace("-", "_")).\
        apply(partial(gross_area_subject_above, a_source="GPGSource"))
    df['gross_floor_area_under_ground'] = df['Unique Code'].apply(lambda x: x.replace("-", "_")).\
        apply(partial(gross_area_subject_under, a_source="GPGSource"))

    df['building_element'] = df['Unique Code'].apply(lambda x: x.replace("-", "_")).\
        apply(construction_element_subject)


def harmonize_data(data, **kwargs):
    namespace = kwargs['namespace']
    user = kwargs['user']
    config = kwargs['config']
    n = Namespace(namespace)
    mapper = Mapper(config['source'], n)
    df = pd.DataFrame.from_records(data)
    log_string("preparing df", mongo=False)
    df = df.applymap(decode_hbase)
    clean_dataframe(df)
    log_string("generating rdf", mongo=False)
    g = generate_rdf(mapper.get_mappings("all"), df)
    log_string("saving", mongo=False)
    save_rdf_with_source(g, config['source'], config['neo4j'])
