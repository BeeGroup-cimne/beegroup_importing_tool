from urllib.parse import urlparse

import rdflib
from neo4j import GraphDatabase
from rdflib import Graph, RDF, URIRef
import settings
from utils.rdf_utils.ontology.namespaces_definition import Bigg


multi_value_classes = {
    Bigg.LocationInfo: {Bigg.hasAddressCountry: None, Bigg.hasAddressProvince: None, Bigg.hasAddressCity: None,
                        Bigg.hasAddressClimateZone: None},
    Bigg.CadastralInfo: {Bigg.hasLandType: None},
    Bigg.Building: {Bigg.hasBuildingConstructionType: None, Bigg.hasBuildingOwnership: None},
    Bigg.BuildingSpace: {Bigg.hasBuildingSpaceUseType: None, Bigg.hasIndoorQualityPerception: None,
                         Bigg.hasArea: Bigg.hasAreaType}
}

# def __neo4j_with_source(ses, source, data_links={}):
#     for subject, links in data_links.items():
#         n_query = f"""
#             Match (n{{uri: "{subject}"}})
#         """
#         for link_attr in links:
#             l, o, s_diff = link_attr
#             n_query += f"""
#                 WITH n
#                 MATCH (s{{uri: "{o}"}})
#                 WITH n, s
#                     OPTIONAL MATCH (n)-[l:{l}]->(s) WHERE l.source is null DELETE l
#                 WITH n, s
#                 MERGE (n)-[l:{l}{{source: "{source}"}}]->(s)
#                 WITH n, l, s
#                 SET
#                 l.selected = CASE
#                     WHEN EXISTS(l.selected) THEN l.selected
#                     ELSE s.ttt__{s_diff}__selected[0]
#                     END
#                 REMOVE s.ttt__{s_diff}__selected
#             """
#         ses.run(n_query)


def __set_source_link(neo, source, data_link, prop_node):
    for l in data_link:
        with neo.session() as session:
            session.run(f"""
            MATCH(s)-[r:`{l}@{source}`]-(d) MERGE (s)-[:{l}{{source:"{source}"}}]-(d) delete r
            """)

    for cln, lp in prop_node.items():
        for l in lp:
            elem_list = [l]
            elem_list += [f"{l}@{x}" for x in settings.sources_priorities]
            with neo.session() as session:
                session.run(f"""
                call{{ 
                    Match(n:{cln}) unwind {elem_list} as key return collect(n[key]) as list, n}} set n.{l} = list[0]
                """)

    with neo.session() as session:
        namespaces = session.run(f"""
        MATCH (n:`_NsPrefDef`)
        WITH keys(n) as k, n
        RETURN n
        """).single().data().get('n')
    namespaces_i = {}
    for k, v in namespaces.items():
        namespaces_i[v] = k

    source_order = "CASE r.source " + " ".join([f"WHEN '{s}' THEN {i}" for i, s in enumerate(settings.sources_priorities)]) + " END as sort"

    for class_, attr_list in multi_value_classes.items():
        cls_ns, cls = class_.split('#')
        cls_ns = namespaces_i[cls_ns+"#"]
        for attribute, special in attr_list.items():
            attr_ns, attr = attribute.split('#')
            attr_ns = namespaces_i[attr_ns + "#"]
            selection_query = f"""
                MATCH (n:{cls_ns}__{cls})-[r:{attr_ns}__{attr}]->()"""
            special_node = ""
            if special:
                sp_ns, sp_r = special.split("#")
                sp_ns = namespaces_i[sp_ns + "#"]
                selection_query += f"""-[:{sp_ns}__{sp_r}]->(special)"""
                special_node = """special, """
            selection_query += f"""
                WITH {special_node} n, r, {source_order}
                WITH {special_node} n, r ORDER BY sort
                WITH {special_node} n, collect(r) as rela
                FOREACH (p in tail(rela) | set p.selected=false) 
                WITH rela 
                SET head(rela).selected=true
            """
            with neo.session() as session:
                session.run(selection_query)


def __neo4j_import__(ses, v):
    f = f"""CALL n10s.rdf.import.inline('{v}','Turtle')"""
    result = ses.run(f)
    resp = result.single()
    return resp


def save_rdf_with_source(graph, source, connection):
    if source not in settings.sources_priorities:
        raise Exception("Error, add source to priority list in settings")
    neo = GraphDatabase.driver(**connection)
    with neo.session() as session:
        namespaces = session.run(f"""
        MATCH (n:`_NsPrefDef`)
        WITH keys(n) as k, n
        RETURN n
        """).single().data().get('n')
    neo.close()
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
    neo = GraphDatabase.driver(**connection)
    with neo.session() as session:
        tty = __neo4j_import__(session, v)
        print(tty)
    __set_source_link(neo, source, data_link, prop_node)
    neo.close()



def link_devices_with_source(df, ns, neo4j_connection):
    df_temp = df[["source_id", "device_subject"]]
    df_temp.loc[:, "device_subject"] = df_temp["device_subject"].apply(ns.__getattr__).apply(str)
    for limit in range(0, len(df_temp), 50):
        links_dict = df_temp.iloc[limit:limit+50][["source_id", "device_subject"]].to_dict(orient="records")
        neo = GraphDatabase.driver(**neo4j_connection)
        with neo.session() as session:
            session.run(f"""
            CALL {{ RETURN apoc.convert.fromJsonList("{links_dict}") as links}}
            UNWIND links AS items
            MATCH (source) WHERE id(source)= items.source_id
            MATCH (device) WHERE device.uri=items.device_subject
            Merge (source)<-[:importedFromSource]-(device)
            WITH source, device
            UNWIND labels(source) AS s
            WITH s , device
            WHERE s =~ ".*Source"
            SET device.source = s""")
        neo.close()
        print(limit)


    # for _, device in df.iterrows():
    #     neo = GraphDatabase.driver(**neo4j_connection)
    #     with neo.session() as session:
    #         session.run(
    #             f"""
    #                 MATCH (source) WHERE id(source)={device.source_id}
    #                 MATCH (device) WHERE device.uri="{ns[device.device_subject]}"
    #                 Merge (source)<-[:importedFromSource]-(device)
    #                 WITH source, device
    #                 UNWIND labels(source) AS s
    #                 WITH s , device
    #                 WHERE s =~ ".*Source"
    #                 SET device.source = s
    #                 RETURN device""")
    #     neo.close()
    # query_devices = f"""
    #            PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    #            PREFIX bigg:<{str(Bigg)}>
    #            SELECT DISTINCT ?nif
    #            WHERE {{
    #                ?sub rdf:type bigg:Device .
    #            }}
    #         """
    # r_devices = g.query(query_devices)
    # for subject in r_devices:
    #     neo = GraphDatabase.driver(**neo4j_connection)
    #     with neo.session() as session:
    #         session.run(
    #             f"""
    #                 MATCH (source) WHERE id(source)={source_id}
    #                 MATCH (device) WHERE device.uri="{str(subject[0])}"
    #                 Merge (source)<-[:importedFromSource]-(device)
    #                 WITH source, device
    #                 UNWIND labels(source) AS s
    #                 WITH s , device
    #                 WHERE s =~ ".*Source"
    #                 SET device.source = s
    #                 RETURN device""")
    #         neo.close()