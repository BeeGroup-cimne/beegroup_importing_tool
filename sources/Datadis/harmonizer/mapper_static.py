import pandas as pd
from neo4j import GraphDatabase
from rdflib import Namespace
from .Datadis_mapping import Mapping
from utils.rdf_utils.rdf_functions import generate_rdf
from utils.rdf_utils.save_rdf import save_rdf_with_source, link_devices_with_source
from utils.data_transformations import *
from utils.utils import log_string


def harmonize_data(data, **kwargs):
    namespace = kwargs['namespace']
    user = kwargs['user']
    config = kwargs['config']

    # get codi_ens from neo4j
    df = pd.DataFrame.from_records(data)

    neo = GraphDatabase.driver(**config['neo4j'])
    with neo.session() as ses:
        datadis_source = ses.run(f"""
              Match (u:ns0__UtilityPointOfDelivery)<-[*]-(b:ns0__Building)<-[*]-
              (o:ns0__Organization{{ns0__userId:"{user}"}})
              return u.ns0__pointOfDeliveryIDFromUser , b.ns0__buildingIDFromOrganization
              """
                                 )
        cups_code = {x['u.ns0__pointOfDeliveryIDFromUser']: x['b.ns0__buildingIDFromOrganization']
                     for x in datadis_source}

        df['decoded_cups'] = df.cups.apply(decode_hbase)
        df['NumEns'] = df.decoded_cups.apply(lambda x: cups_code[x] if x in cups_code else None)
        linked_supplies = df[df["NumEns"].isna() == False]
        unlinked_supplies = df[df["NumEns"].isna()]
        for linked, df in [("linked", linked_supplies), ("unlinked", unlinked_supplies)]:
            for group, supply_by_group in df.groupby("nif"):
                log_string(f"generating_rdf for {group}, {linked},{len(supply_by_group)}")
                if supply_by_group.empty:
                    continue
                datadis_source = ses.run(
                    f"""Match (n: DatadisSource{{username:"{decode_hbase(group)}"}}) return n""").single()
                datadis_source = datadis_source.get("n").id
                log_string("generating rdf")
                n = Namespace(namespace)
                mapping = Mapping(config['source'], n)
                g = generate_rdf(mapping.get_mappings(linked), supply_by_group)
                log_string("saving to neo4j")
                save_rdf_with_source(g, config['source'], config['neo4j'])
                log_string("linking with source")
                link_devices_with_source(g, datadis_source, config['neo4j'])
