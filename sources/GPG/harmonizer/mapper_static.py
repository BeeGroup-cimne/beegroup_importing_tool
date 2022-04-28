import pandas as pd
import rdflib
from thefuzz import process
from neo4j import GraphDatabase
from rdflib import Namespace, Graph
from slugify import slugify

import settings
from utils.rdf_utils.ontology.namespaces_definition import Bigg
from utils.rdf_utils.rdf_functions import generate_rdf
from utils.rdf_utils.save_rdf import save_rdf_with_source
from .GPG_mapping import Mapper

# get namespaces
bigg = settings.namespace_mappings['bigg']


def _harmonize_organization_names(g, user_id, namespace, mapper, neo4j_conn):
    # Get all existing Organizations typed department
    neo = GraphDatabase.driver(**neo4j_conn)
    with neo.session() as s:
        organization_name = s.run(f"""
        MATCH (m:{bigg}__Organization {{userID: "{user_id}"}}) 
        return m.{bigg}__organizationName
        """).single().value()[0]
        organization_names = s.run(f"""
         MATCH 
         (m:{bigg}__Organization {{userID: "{user_id}"}})-[:{bigg}__hasSubOrganization *]->
         (n:{bigg}__Organization{{{bigg}__organizationDivisionType: ["Department"]}})
         RETURN n.uri
         """)
        dep_uri = [x.value() for x in organization_names]
    # Get all organizations in rdf graph using sparql
    query_department = f"""
        PREFIX rdf:<http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX bigg:<{str(Bigg)}>
        SELECT DISTINCT ?sub
        WHERE {{
            ?sub rdf:type bigg:Organization .
            ?sub bigg:organizationDivisionType "Department" .
        }}
     """
    r_dep = g.query(query_department)
    g_others = generate_rdf(mapper.get_mappings("other"), pd.DataFrame())
    g += g_others
    other_subj = list(set(g_others.subjects()))[0]
    main_org_subject = namespace[slugify(organization_name)]
    g.add((rdflib.URIRef(main_org_subject), Bigg.hasSubOrganization, other_subj))
    for dep_org in r_dep:
        query = str(dep_org[0])
        choices = dep_uri
        # Get a list of matches ordered by score, default limit to 5
        match, score = process.extractOne(query, choices)
        if score > 90:
            g2 = Graph()
            for s, p, o in g.triples((dep_org[0], None, None)):
                g2.add((rdflib.URIRef(match), p, o))
            g.remove((dep_org[0], None, None))
            g += g2
        else:
            g2 = Graph()
            for s, p, o in g.triples((dep_org[0], None, None)):
                g2.add((other_subj, p, o))
            g.remove((dep_org[0], None, None))
            g += g2
    return g


def harmonize_data(data, **kwargs):
    namespace = kwargs['namespace']
    user = kwargs['user']
    config = kwargs['config']
    organizations = kwargs['organizations'] if 'organizations' in kwargs else False
    n = Namespace(namespace)
    mapper = Mapper(config['source'], n)
    df = pd.DataFrame.from_records(data)
    if organizations:
        print("A")
        g = generate_rdf(mapper.get_mappings("all"), df)
        print("B")
        g = _harmonize_organization_names(g, user, n, mapper, config['neo4j'])
    else:
        print("C")
        g = generate_rdf(mapper.get_mappings("buildings"), df)
    print("D")
    save_rdf_with_source(g, config['source'], config['neo4j'])
