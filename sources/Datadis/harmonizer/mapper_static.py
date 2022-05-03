import pandas as pd
from neo4j import GraphDatabase
from rdflib import Namespace
from .Datadis_mapping import Mapping
from utils.rdf_utils.rdf_functions import generate_rdf
from utils.rdf_utils.save_rdf import save_rdf_with_source, link_devices_with_source
from utils.data_transformations import *
import settings
from utils.utils import log_string


bigg = settings.namespace_mappings['bigg']


province_find = partial(fuzzy_dictionary_match,
        dictionary=["utils/rdf_utils/ontology/dictionaries/province.ttl"],
        predicates=['ns1:name'])


def city_find(province):
    prequery = f"""SELECT ?s ?p ?o WHERE {{?s ?p ?o . ?s ns1:parentADM2 <{province}>}}"""
    city_find = partial(fuzzy_dictionary_match,
                        dictionary=["utils/rdf_utils/ontology/dictionaries/municipality.ttl",
                                    "utils/rdf_utils/ontology/dictionaries/province.ttl"],
                        predicates=['ns1:name'],
                        prequery=prequery)
    return city_find


def prepare_df_clean_all(df):
    df['device_subject'] = df.cups.apply(partial(device_subject, source="DatadisSource"))


def prepare_df_clean_linked(df):
    df['location_subject'] = df.NumEns.apply(id_zfill).apply(location_info_subject)
    df['hasAddressProvince'] = df.province.apply(province_find)
    for g, grouped in df.groupby("hasAddressProvince"):
        df['hasAddressCity'] = grouped.municipality.apply(city_find(g))
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
        datadis_source = ses.run(f"""
            Match (u:{bigg}__UtilityPointOfDelivery)<-[:{bigg}__hasSpace|{bigg}__hasUtilityPointOfDelivery *]-
                  (b:{bigg}__Building)<-[:{bigg}__managesBuilding|{bigg}__hasSubOrganization *]-
                  (o:{bigg}__Organization{{userID:"{user}"}}) 
            RETURN u.{bigg}__pointOfDeliveryIDFromOrganization as CUPS, b.{bigg}__buildingIDFromOrganization as NumEns
            """
        )
        cups_code = {x['CUPS'][0]: x['NumEns'][0]
                     for x in datadis_source}
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
