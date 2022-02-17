from urllib.parse import urlparse

import rdflib
from neo4j import GraphDatabase
from rdflib import Graph, RDF

from utils.rdf_utils.bigg_definition import Bigg
from utils.utils import log_string

multi_value_classes = [Bigg.LocationInfo, Bigg.CadastralInfo, Bigg.Building, Bigg.BuildingSpace]


def __neo4j_import__(ses, v):
    f = f"""CALL n10s.rdf.import.inline('{v}','Turtle')"""
    result = ses.run(f)
    return result.single()


def save_rdf_with_source(graph, source, connection):
    neo = GraphDatabase.driver(**connection)
    # only multi_value_classes will have "multiple_values"
    multi_value_subjects = {}
    for class_ in multi_value_classes:
        multi_value_subjects[class_] = list(set(graph.subjects(RDF.type, class_)))
    g2 = Graph()
    for class_, list_ in multi_value_subjects.items():
        if not list_:
            continue
        # get and parse the elements existing in DB
        parsed_type = urlparse(class_)
        with neo.session() as session:
            neo_data = session.run(f"Match (n: ns0__{parsed_type.fragment}) return n")
            if neo_data:
                neo_elements = {neo_element['n'].get("uri"): neo_element for neo_element in neo_data}
            else:
                neo_elements = {}
        for subject in list_:
            try:
                neo_element = neo_elements[str(subject)]
            except IndexError:
                neo_element = None
            except KeyError:
                neo_element = None
            for s, p, o in graph.triples((subject, None, None)):
                if isinstance(o, rdflib.Literal):
                    parsed_uri = urlparse(p)
                    if not neo_element or not neo_element['n'].get(f'ns0__{parsed_uri.fragment}'):
                        g2.add((s, p, o))
                        g2.add((s, p + '__selected', rdflib.Literal(source)))
                    g2.add((s, p + f"__{source}", o))
                else:
                    g2.add((s, p, o))
            graph.remove((subject, None, None))

    g2 += graph
    v = g2.serialize(format="ttl")
    v = v.replace('\\"', "`")
    v = v.replace("'", "`")

    with neo.session() as session:
        tty = __neo4j_import__(session, v)
        print(tty)


def link_devices_with_source(g, source_id, neo4j_connection):
    query_devices = f"""
               PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
               PREFIX bigg:<{str(Bigg)}>
               SELECT DISTINCT ?sub
               WHERE {{
                   ?sub rdf:type bigg:Device .
               }}    
            """
    r_devices = g.query(query_devices)
    neo = GraphDatabase.driver(**neo4j_connection)
    with neo.session() as session:
        for subject in r_devices:
            session.run(
                f"""
                    MATCH (source) WHERE id(source)={source_id}
                    MATCH (device) WHERE device.uri="{str(subject[0])}"
                    Merge (source)<-[:ns0__importedFromSource]-(device)
                    RETURN device""")
