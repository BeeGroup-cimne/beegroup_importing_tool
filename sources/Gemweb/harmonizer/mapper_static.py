from urllib.parse import urlparse
import pandas as pd
from neo4j import GraphDatabase
from rdflib import Namespace
import settings
from .Gemweb_mapping import Mapping
from utils.rdf_utils.rdf_functions import generate_rdf
from utils.data_transformations import decode_hbase
from utils.rdf_utils.save_rdf import save_rdf_with_source, link_devices_with_source

bigg = settings.namespace_mappings['bigg']


def harmonize_data(data, **kwargs):
    namespace = kwargs['namespace']
    user = kwargs['user']
    config = kwargs['config']

    neo = GraphDatabase.driver(**config['neo4j'])
    n = Namespace(namespace)
    mapping = Mapping(config['source'], n)
    with neo.session() as ses:
        source_id = ses.run(
            f"""Match (o: {bigg}__Organization{{userID: "{user}"}})-[:hasSource]->(s:GemwebSource) 
                return id(s)""")
        source_id = source_id.single().get("id(s)")

    with neo.session() as ses:
        buildings_neo = ses.run(
            f"""Match (n:{bigg}__Building)<-[:{bigg}__hasSubOrganization|{bigg}__managesBuilding *]-
            (o:{bigg}__Organization)-[:hasSource]->(s:GemwebSource) 
                Where id(s)={source_id} 
                return n.uri""")
        ids_ens = list(set([urlparse(x.get("n.uri")).fragment.split("-")[1] for x in buildings_neo]))
    # create num_ens column with parsed values in df
    df = pd.DataFrame.from_records(data)
    df['num_ens'] = df['codi'].apply(lambda x: decode_hbase(x).zfill(5))

    # get all devices with linked buildings
    df_linked = df[df['num_ens'].isin([str(i) for i in ids_ens])]

    g = generate_rdf(mapping.get_mappings("linked"), df_linked)
    save_rdf_with_source(g, config['source'], config['neo4j'])

    # link devices from G to the source
    link_devices_with_source(g, source_id, config['neo4j'])

    df_unlinked = df[df['num_ens'].isin([str(i) for i in ids_ens]) == False]
    g2 = generate_rdf(mapping.get_mappings("unlinked"), df_unlinked)
    save_rdf_with_source(g2, config['source'], config['neo4j'])
    link_devices_with_source(g2, source_id, config['neo4j'])
