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
            g.parse(f"{DICTIONARIES}/{f}", format="ttl")
            v = g.serialize(format="ttl")
            v = v.replace('\\"', "`")
            v = re.sub(r"\"[^\"]*\"", lambda x: x.group(0).replace("'", "%27"), v)
            v = re.sub(r"<[^>]*>", lambda x: x.group(0).replace("'", "%27"), v)
            print(save_rdf.__neo4j_import__(session, v))
            namespaces = session.run(f"""
                MATCH (n:`_NsPrefDef`)
                WITH keys(n) as k, n
                RETURN n
                    """).single().data().get('n')
            namespaces_i = {}
            for k, v in namespaces.items():
                v = v[:-1]
                namespaces_i[v] = k
            print(namespaces_i)

            for s, p in g.subject_predicates(None):
                o_list = list(g.objects(s, p))
                if any(["'" in o for o in o_list]):
                    try:
                        ns, f = str(p).split("#")
                    except:
                        pp = str(p).split("/")
                        ns = "/".join(pp[:-1])
                        f = pp[-1]
                    o_value = []
                    for o in o_list:
                        try:
                            lan = o.language
                        except:
                            lan = None
                        if "\"" in o:
                            o = str(o).replace("\"", "'")
                        if lan:
                            o_value.append(f"{o}@{lan}")
                        else:
                            o_value.append(str(o))
                    session.run(f"""
                    Match(n{{uri:"{s}"}})
                    SET n.{namespaces_i[ns]}__{f}={o_value if len(o_value) >= 1 and lan else '"' + str(o_value[0]) + '"'}
                    """)
            #
            # v = v.replace("'", "`")

