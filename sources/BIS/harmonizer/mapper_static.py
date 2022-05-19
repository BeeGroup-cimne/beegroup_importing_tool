
from neo4j import GraphDatabase
from rdflib import Namespace, Graph
from slugify import slugify

import settings
from utils.data_transformations import *
from utils.rdf_utils.ontology.namespaces_definition import Bigg, bigg_enums
from utils.rdf_utils.rdf_functions import generate_rdf
from utils.rdf_utils.save_rdf import save_rdf_with_source
from .GPG_mapping import Mapper
from .transform_functions import *

# get namespaces
bigg = settings.namespace_mappings['bigg']


def harmonize_organizations(x, map):
    resp = set()
    for xx in x:
        resp.add(map[xx])
    return list(resp)


def _organization_map(series, orgs, default):
    x = set()
    for item in series:
        for xx in item:
            x.add(xx)

    resp = {}
    for xx in x:
        query = slugify(xx)
        match, score = process.extractOne(query, orgs.keys())
        if score > 90:
            resp[xx] = orgs[match]
        else:
            resp[xx] = default
    return resp


def _get_fuzz_params(user_id, neo4j_conn):
    # Get all existing Organizations typed department
    neo = GraphDatabase.driver(**neo4j_conn)
    with neo.session() as s:
        organization_name = s.run(f"""
        MATCH (m:{bigg}__Organization {{userID: "{user_id}"}}) 
        return m.uri
        """).single().value()
        organization_names = s.run(f"""
         MATCH 
         (m:{bigg}__Organization {{userID: "{user_id}"}})-[:{bigg}__hasSubOrganization *]->
         (n:{bigg}__Organization{{{bigg}__organizationDivisionType: ["Department"]}})
         RETURN n.uri
         """)
        dep_uri = {x.value().split("#")[1]: x.value().split("#")[1] for x in organization_names}
    return {"orgs": dep_uri, "default": organization_name.split("#")[1]}


def fuzz_departments(df, user_id, neo4j):
    df['department_organization'] = df['Departament_Assig_Adscrip'].apply(lambda x: x.split(";")). \
        apply(lambda x: [clean_department(s) for s in x])
    fparams = _get_fuzz_params(user_id, neo4j)
    org_map = _organization_map(df['department_organization'], **fparams)
    harmonize_deps = partial(harmonize_organizations, map=org_map)
    df['department_organization'] = df['department_organization'].apply(harmonize_deps).apply(lambda x: ";".join(x))


def clean_dataframe(df):
    df['building_organization'] = df['Num_Ens_Inventari'].apply(id_zfill).apply(building_department_subject)
    df['building'] = df['Num_Ens_Inventari'].apply(id_zfill).apply(building_subject)
    df['buildingIDFromOrganization'] = df['Num_Ens_Inventari'].apply(id_zfill)
    df['location_info'] = df['Num_Ens_Inventari'].apply(id_zfill).apply(location_info_subject)
    province_dic = load_dic(["utils/rdf_utils/ontology/dictionaries/province.ttl"])
    province_fuzz = partial(fuzzy_dictionary_match,
                            map_dict=fuzz_params(province_dic, ['ns1:name']),
                            default=None
                            )
    unique_prov = df['Provincia'].unique()
    prov_map = {k: province_fuzz(k) for k in unique_prov}
    df['hasAddressProvince'] = df['Provincia'].map(prov_map)

    municipality_dic = load_dic(["utils/rdf_utils/ontology/dictionaries/municipality.ttl"])
    for prov, df_group in df.groupby('hasAddressProvince'):
        municipality_fuzz = partial(fuzzy_dictionary_match,
                                    map_dict=fuzz_params(
                                        municipality_dic,
                                        ['ns1:name'],
                                        filter_query=f"SELECT ?s ?p ?o WHERE{{?s ?p ?o . ?s ns1:parentADM2 <{prov}>}}"
                                        ),
                                    default=None
                                    )
        unique_city = df_group.Municipi.unique()
        city_map = {k: municipality_fuzz(k) for k in unique_city}
        df.loc[df['hasAddressProvince']==prov, 'hasAddressCity'] = df_group.Municipi.map(city_map)

    df['cadastral_info'] = df['Ref_Cadastral'].apply(validate_ref_cadastral)
    df['building_space'] = df['Num_Ens_Inventari'].apply(id_zfill).apply(building_space_subject)

    building_type_taxonomy = get_taxonomy_mapping(
        taxonomy_file="sources/GPG/harmonizer/BuildingUseTypeTaxonomy.xls",
        default="Other")

    df['hasBuildingSpaceUseType'] = df['Tipus_us'].apply(lambda x: ast.literal_eval(x)[-1]).map(building_type_taxonomy). \
        apply(partial(to_object_property, namespace=bigg_enums))
    df['gross_floor_area'] = df['Num_Ens_Inventari'].apply(id_zfill).\
        apply(partial(gross_area_subject, a_source="GPGSource"))
    df['gross_floor_area_above_ground'] = df['Num_Ens_Inventari'].\
        apply(id_zfill).apply(partial(gross_area_subject_above, a_source="GPGSource"))
    df['gross_floor_area_under_ground'] = df['Num_Ens_Inventari'].\
        apply(id_zfill).apply(partial(gross_area_subject_under, a_source="GPGSource"))

    df['building_element'] = df['Num_Ens_Inventari'].apply(id_zfill).apply(construction_element_subject)


def harmonize_data(data, **kwargs):
    namespace = kwargs['namespace']
    user = kwargs['user']
    config = kwargs['config']
    organizations = kwargs['organizations'] if 'organizations' in kwargs else False
    n = Namespace(namespace)
    mapper = Mapper(config['source'], n)
    df = pd.DataFrame.from_records(data)
    print("preparing df")
    df = df.applymap(decode_hbase)
    clean_dataframe(df)
    print("generating rdf")
    if organizations:
        print("maching organizations")
        fuzz_departments(df, user, config['neo4j'])
        g = generate_rdf(mapper.get_mappings("all"), df)
    else:
        g = generate_rdf(mapper.get_mappings("buildings"), df)
    print("saving")
    save_rdf_with_source(g, config['source'], config['neo4j'])
