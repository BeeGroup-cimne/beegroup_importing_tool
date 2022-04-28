import os
import re

import rdflib
from neo4j import GraphDatabase

import settings
import utils.utils
from utils.rdf_utils import save_rdf

DICTIONARIES = "utils/rdf_utils/ontology/dictionaries"

if __name__ == "__main__":
    config = utils.utils.read_config(settings.conf_file)
    neo = GraphDatabase.driver(**config['neo4j'])
    with neo.session() as session:
        for f in os.listdir(DICTIONARIES):
            print(f)
            g = rdflib.Graph()
            g.load(f"{DICTIONARIES}/{f}", format="ttl")
            v = g.serialize(format="ttl")
            v = v.replace('\\"', "`")
            v = re.sub(r"\"[^\"]*\"", lambda x: x.group(0).replace("'", "%27"), v)
            v = re.sub(r"<[^>]*>", lambda x: x.group(0).replace("'", "%27"), v)

            #
            # v = v.replace("'", "`")
            print(save_rdf.__neo4j_import__(session, v))
