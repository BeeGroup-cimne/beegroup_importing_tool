import pandas as pd
from neo4j import GraphDatabase
from rdflib import Namespace

from utils.neo4j import get_cups_id_link
from .Datadis_mapping import Mapping
from utils.rdf_utils.rdf_functions import generate_rdf
from utils.rdf_utils.save_rdf import save_rdf_with_source, link_devices_with_source
from utils.data_transformations import *
import settings
from utils.utils import log_string


bigg = settings.namespace_mappings['bigg']


def prepare_df_clean_all(df):
    df['device_subject'] = df.cups.apply(partial(device_subject, source="DatadisSource"))


def prepare_df_clean_linked(df):
    df['location_subject'] = df.NumEns.apply(id_zfill).apply(location_info_subject)
    province_dic = load_dic(["utils/rdf_utils/ontology/dictionaries/province.ttl"])
    province_fuzz = partial(fuzzy_dictionary_match,
                           map_dict=fuzz_params(province_dic, ['ns1:name']),
                           default=None)
    unique_prov = df['province'].unique()
    province_map = {x: province_fuzz(x) for x in unique_prov}
    df['hasAddressProvince'] = df.province.map(province_map)

    municipality_dic = load_dic(["utils/rdf_utils/ontology/dictionaries/municipality.ttl"])
    for prov_k, prov_uri in province_map.items():
        if prov_uri is None:
            df.loc[df['province'] == prov_k, 'hasAddressCity'] = None
            continue
        grouped = df.groupby("province").get_group(prov_k)
        city_fuzz = partial(fuzzy_dictionary_match,
                            map_dict=fuzz_params(
                                municipality_dic,
                                ['ns1:name'],
                                filter_query=f"""SELECT ?s ?p ?o WHERE {{?s ?p ?o . ?s ns1:parentADM2 <{prov_uri}>}}"""
                            ),
                            default=None)
        unique_city = grouped.municipality.unique()
        city_map = {k: city_fuzz(k) for k in unique_city}
        df.loc[df['province'] == prov_k, 'hasAddressCity'] = grouped.municipality.map(city_map)
    df['building_space_subject'] = df.NumEns.apply(id_zfill).apply(building_space_subject)
    df['utility_point_subject'] = df.cups.apply(delivery_subject)


def harmonize_data(data, **kwargs):
    namespace = kwargs['namespace']
    user = kwargs['user']
    config = kwargs['config']

    df = pd.DataFrame.from_records(data)
    df = df.applymap(decode_hbase)

    # get codi_ens from neo4j
    neo = GraphDatabase.driver(**config['neo4j'])
    with neo.session() as ses:
        cups_code = get_cups_id_link(ses, user)

    df['NumEns'] = df.cups.map(cups_code)

    prepare_df_clean_all(df)
    linked_supplies = df[df["NumEns"].isna()==False]
    unlinked_supplies = df[df["NumEns"].isna()]

    for linked, df in [("linked", linked_supplies), ("unlinked", unlinked_supplies)]:
        if linked == "linked":
            prepare_df_clean_linked(df)
        for group, supply_by_group in df.groupby("nif"):
            # log_string(f"generating_rdf for {group}, {linked},{len(supply_by_group)}")
            if supply_by_group.empty:
                continue
            with neo.session() as ses:
                datadis_source = ses.run(
                    f"""Match (n: DatadisSource{{username:"{group}"}}) return n""").single()
                datadis_source = datadis_source.get("n").id
            # log_string("generating rdf")
            n = Namespace(namespace)
            mapping = Mapping(config['source'], n)
            g = generate_rdf(mapping.get_mappings(linked), supply_by_group)
            # log_string("saving to neo4j")
            save_rdf_with_source(g, config['source'], config['neo4j'])
            # log_string("linking with source")
            link_devices_with_source(g, datadis_source, config['neo4j'])
