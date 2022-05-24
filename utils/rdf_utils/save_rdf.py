from urllib.parse import urlparse

import rdflib
from neo4j import GraphDatabase
from rdflib import Graph, RDF, URIRef

from utils.rdf_utils.ontology.namespaces_definition import Bigg


def get_area_type_from_uri(uri):
    return uri.split("#")[1].split("-")[1]


multi_value_classes = {
    Bigg.LocationInfo: {Bigg.hasAddressCountry: [], Bigg.hasAddressProvince: [], Bigg.hasAddressCity: [],
                        Bigg.hasAddressClimateZone: []},
    Bigg.CadastralInfo: {Bigg.hasLandType: []},
    Bigg.Building: {Bigg.hasBuildingConstructionType: [], Bigg.hasBuildingOwnership: []},
    Bigg.BuildingSpace: {Bigg.hasBuildingSpaceUseType: [], Bigg.hasIndoorQualityPerception: [],
                         Bigg.hasArea: [get_area_type_from_uri]}
}
sources = ["GPG", "BIS", "gemweb", "DatadisSource", "Genercat", "Nedgia", "Weather"]

def __neo4j_with_source(ses, source, data_links={}):
    for subject, links in data_links.items():
        n_query = f"""
            Match (n{{uri: "{subject}"}})
        """
        for link_attr in links:
            l, o, s_diff = link_attr
            n_query += f"""
                WITH n
                MATCH (s{{uri: "{o}"}})
                WITH n, s
                    OPTIONAL MATCH (n)-[l:{l}]->(s) WHERE l.source is null DELETE l
                WITH n, s
                MERGE (n)-[l:{l}{{source: "{source}"}}]->(s)
                WITH n, l, s
                SET 
                l.selected = CASE 
                    WHEN EXISTS(l.selected) THEN l.selected
                    ELSE s.ttt__{s_diff}__selected[0]
                    END
                REMOVE s.ttt__{s_diff}__selected 
            """
        ses.run(n_query)


def __set_source_link(session, source, data_link, prop_node):
    for l in data_link:
        session.run(f"""
        MATCH(s)-[r:`{l}@{source}`]-(d) MERGE (s)-[:{l}{{source:"{source}"}}]-(d) delete r
        """)

    for cln, lp in prop_node.items():
        for l in lp:
            elem_list = [l]
            elem_list += [f"{l}@{x}" for x in sources]
            session.run(f"""
            call{{ 
                Match(n:{cln}) unwind {elem_list} as key return collect(n[key][0]) as list, n}} set n.{l} = list
            """)

def __neo4j_import__(ses, v):
    f = f"""CALL n10s.rdf.import.inline('{v}','Turtle')"""
    result = ses.run(f)
    resp = result.single()
    return resp


def save_rdf_with_source(graph, source, connection):
    neo = GraphDatabase.driver(**connection)
    with neo.session() as session:
        namespaces = session.run(f"""
        MATCH (n:`_NsPrefDef`)
        WITH keys(n) as k, n
        RETURN n
        """).single().data().get('n')
    namespaces_i = {}
    for k, v in namespaces.items():
        namespaces_i[v] = k

    multi_value_subjects = {}
    for class_ in multi_value_classes.keys():
        multi_value_subjects[class_] = list(set(graph.subjects(RDF.type, class_)))
    data_link = set()
    prop_node = {}
    for class_, list_ in multi_value_subjects.items():
        if not list_:
            continue
        try:
            ns, cln = class_.split("#")
            ns += "#"
            cln = f'{namespaces_i[ns]}__{cln}'
        except:
            cln = None
        for subject in list_:
            gtemp = Graph()
            for s, p, o in graph.triples((subject, None, None)):
                try:
                    ns, att = p.split("#")
                    ns += "#"
                    att = f'{namespaces_i[ns]}__{att}'
                except:
                    att = None
                if isinstance(o, rdflib.Literal):
                    if att:
                        try:
                            prop_node[cln].add(att)
                        except:
                            prop_node[cln] = set()
                            prop_node[cln].add(att)
                    gtemp.add((s, rdflib.URIRef(f"{p}@{source}"), o))
                elif p in multi_value_classes[class_].keys():
                    if att:
                        data_link.add(att)
                    gtemp.add((s, rdflib.URIRef(f"{p}@{source}"), o))
                else:
                    gtemp.add((s, p, o))
            graph.remove((subject, None, None))
            graph += gtemp
    v = graph.serialize(format="ttl")
    v = v.replace('\\"', "`")
    v = v.replace("'", "`")
    with neo.session() as session:
        tty = __neo4j_import__(session, v)
        print(tty)
    with neo.session() as session:
        __set_source_link(session, source, data_link, prop_node)


# def save_rdf_with_source(graph, source, connection):
#     neo = GraphDatabase.driver(**connection)
#     # only multi_value_classes will have "multiple_values"
#     multi_value_subjects = {}
#     for class_ in multi_value_classes.keys():
#         multi_value_subjects[class_] = list(set(graph.subjects(RDF.type, class_)))
#     g2 = Graph()
#     data_links = {}
#     for class_, list_ in multi_value_subjects.items():
#         if not list_:
#             continue
#         # get and parse the elements existing in DB
#         parsed_type = urlparse(class_)
#         onto_uri = parsed_type._replace(fragment="").geturl() + "#"
#         with neo.session() as session:
#             ns_neo = session.run(f"""
#             MATCH (n:`_NsPrefDef`)
#             WITH keys(n) as k, n
#             RETURN [s in k where n[s]='{onto_uri}'][0]
#             """).single()
#             neo_data = session.run(f"Match (n: {ns_neo.value()}__{parsed_type.fragment}) return n")
#             neo_rel = session.run(f"Match (n: {ns_neo.value()}__{parsed_type.fragment})-[r{{selected: true}}]->(cn) "
#                                   f"RETURN n, r, cn")
#             if neo_data:
#                 neo_elements = {neo_element['n'].get("uri"): neo_element for neo_element in neo_data}
#             else:
#                 neo_elements = {}
#             if neo_rel:
#                 neo_relations = {}
#                 for s in neo_rel:
#                     attribute = s['r'].type.split('__')[1]
#                     list_values = {urlparse(attr).fragment: attr for attr in multi_value_classes[class_].keys()}
#                     if attribute in list_values.keys():
#                         attr_operations = multi_value_classes[class_][list_values[attribute]]
#                         if attr_operations:
#                             object_difference = s['cn'].get('uri')
#                             for oper in attr_operations:
#                                 object_difference = oper(object_difference)
#                             try:
#                                 neo_relations[f"{s['n'].get('uri')}@{s['r'].type}"].update(
#                                     {object_difference: s}
#                                 )
#                             except KeyError:
#                                 neo_relations[f"{s['n'].get('uri')}@{s['r'].type}"] = \
#                                     {object_difference: s}
#                         else:
#                                 neo_relations[f"{s['n'].get('uri')}@{s['r'].type}"] = s
#             else:
#                 neo_relations = {}
#         index_triple = 0
#         for subject in list_:
#             try:
#                 neo_element = neo_elements[str(subject)]
#             except IndexError:
#                 neo_element = None
#             except KeyError:
#                 neo_element = None
#             for s, p, o in graph.triples((subject, None, None)):
#                 parsed_uri = urlparse(p)
#                 field_ns = parsed_uri._replace(fragment="").geturl() + "#"
#                 with neo.session() as session:
#                     ns_neo = session.run(f"""
#                                         MATCH (n:`_NsPrefDef`)
#                                         WITH keys(n) as k, n
#                                         RETURN [s in k where n[s]='{field_ns}'][0]
#                                         """).single()
#                 if isinstance(o, rdflib.Literal):
#                     if not neo_element or not neo_element['n'].get(f'{ns_neo.value()}__{parsed_uri.fragment}'):
#                         g2.add((s, p, o))
#                         g2.add((s, p + '__selected', rdflib.Literal(source)))
#                     g2.add((s, p + f"__{source}", o))
#                 elif p in [x for x in multi_value_classes[class_]]:
#                     try:
#                         neo_relation = neo_relations[f"{s}@{ns_neo.value()}__{parsed_uri.fragment}"]
#                         if isinstance(neo_relation, dict):
#                             attr_operations = multi_value_classes[class_][p]
#                             o1 = o
#                             for oper in attr_operations:
#                                 o1 = oper(o1)
#                             neo_relation = neo_relation[o1]
#                     except IndexError:
#                         neo_relation = None
#                     except KeyError:
#                         neo_relation = None
#                     subject_diff = urlparse(s).fragment
#                     if not neo_relation:
#                         g2.add((o, URIRef(f"http://ttt.cat#{index_triple}__selected"), rdflib.Literal(True)))
#                     elif neo_relation['r'].get("source") == source:
#                         pass
#                     else:
#                         g2.add((o, URIRef(f"http://ttt.cat#{index_triple}__selected"), rdflib.Literal(False)))
#                     g2.add((s, p, o))
#                     try:
#                         data_links[s].append((f'{ns_neo.value()}__{parsed_uri.fragment}', o, index_triple))
#                     except KeyError:
#                         data_links[s] = [(f'{ns_neo.value()}__{parsed_uri.fragment}', o, index_triple)]
#                 else:
#                     g2.add((s, p, o))
#                 index_triple += 1
#             graph.remove((subject, None, None))
#
#     g2 += graph
#     v = g2.serialize(format="ttl")
#     v = v.replace('\\"', "`")
#     v = v.replace("'", "`")
#
#     with neo.session() as session:
#         tty = __neo4j_import__(session, v)
#         __neo4j_with_source(session, source, data_links)
#         print(tty)


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
                    Merge (source)<-[:importedFromSource]-(device)
                    WITH source, device
                    UNWIND labels(source) AS s 
                    WITH s , device
                    WHERE s =~ ".*Source"
                    SET device.source = s
                    RETURN device""")
