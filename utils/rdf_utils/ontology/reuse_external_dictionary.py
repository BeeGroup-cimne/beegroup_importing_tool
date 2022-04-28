import pandas as pd
import requests
from bs4 import BeautifulSoup
import rdflib
from rdflib import RDF, Namespace, Literal
BIGG = Namespace("http://bigg-project.eu/ontology#")
ALL_QUERY = """SELECT DISTINCT ?s WHERE{ ?s ?p ?o}"""


def align_to_bigg(graph, query, bigg_class):
    for result in graph.query(query):
        for b_clas in bigg_class:
            graph.add((result[0], RDF.type, b_clas))
    return graph


def get_countries_rdf():
    countries_html = requests.get("https://www.geonames.org/countries/").content
    countriesSoup = BeautifulSoup(countries_html, "html.parser")
    countries = [a.contents[0] for a in countriesSoup.select("body table[id=countries] tr > td:nth-of-type(5) > a")]

    all_countries = rdflib.Graph()
    all_countries.namespace_manager.bind("bigg", BIGG)
    for c in countries:
        rdf = requests.get(f"http://api.geonames.org/search?q={c}&featureCode=PCLI&maxRows=10&fuzzy=0.8&type=rdf&username=beegroup").content
        one_country = rdflib.Graph()
        one_country.load(rdf)
        one_country = align_to_bigg(one_country, ALL_QUERY, [BIGG['AddressCountry']])
        all_countries += one_country
    all_countries.serialize("utils/rdf_utils/ontology/dictionaries/countries.ttl", format="ttl")


def create_graph(all_regions, type_adm):
    regions = rdflib.Graph()
    for result in all_regions.query(f"""SELECT ?s ?p ?o WHERE {{?s ?p ?o . ?s geo:featureCode geos:{type_adm}}}"""):
        regions.add(result)
    return regions


def get_adm_rdf(rdf_geonames_file):
    all_regions = rdflib.Graph()
    #load geonames with https
    geos = Namespace("https://www.geonames.org/ontology#")
    geo = Namespace("http://www.geonames.org/ontology#")
    all_regions.namespace_manager.bind("bigg", BIGG)
    all_regions.namespace_manager.bind("geos", geos)
    all_regions.namespace_manager.bind("geo", geo)
    all_regions.load(rdf_geonames_file, format="xml")
    regions = create_graph(all_regions, "A.ADM1")
    province = create_graph(all_regions, "A.ADM2")
    municipality = create_graph(all_regions, "A.ADM3")
    # regions = align_to_bigg(regions, ALL_QUERY, BIGG['AddressCountry'])
    province = align_to_bigg(province, ALL_QUERY, [BIGG['AddressProvince']])
    municipality = align_to_bigg(municipality, ALL_QUERY, [BIGG['AddressCity']])
    regions.serialize("utils/rdf_utils/ontology/dictionaries/regions.ttl", format="ttl")
    province.serialize("utils/rdf_utils/ontology/dictionaries/province.ttl", format="ttl")
    municipality.serialize("utils/rdf_utils/ontology/dictionaries/municipality.ttl", format="ttl")


def align_qudt(qudt_file):
    units = rdflib.Graph()
    units.namespace_manager.bind("bigg", BIGG)
    units.namespace_manager.bind("qudt", Namespace("http://qudt.org/schema/qudt/"))
    units.namespace_manager.bind("quantitykind", Namespace("http://qudt.org/vocab/quantitykind/"))
    units.load(qudt_file, format="ttl")
    # EnergyEfficiencyMeasureInvestmentCurrency, ProjectInvestmentCurrency
    c_query = """SELECT DISTINCT ?s WHERE{ ?s qudt:hasQuantityKind quantitykind:Currency}"""
    units = align_to_bigg(units, c_query,
                          [BIGG['EnergyEfficiencyMeasureInvestmentCurrency'], BIGG['ProjectInvestmentCurrency']])
    # AreaUnits
    a_query = """SELECT DISTINCT ?s WHERE{ ?s qudt:hasQuantityKind quantitykind:Area}"""
    units = align_to_bigg(units, a_query, [BIGG['AreaUnitOfMeasurement']])
    # MeasurementUnit
    units = align_to_bigg(units, ALL_QUERY, [BIGG['MeasurementUnit']])
    units.serialize("utils/rdf_utils/ontology/dictionaries/units.ttl", format="ttl")


#get_countries_rdf()
#get_adm_rdf("/Users/eloigabal/Downloads/all-geonames-rdf-clean.txt")
align_qudt("/Users/eloigabal/Downloads/qudtUnits.ttl")