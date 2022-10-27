import sys

import rdflib
import requests
from bs4 import BeautifulSoup
from rdflib import RDF, Namespace

BIGG = Namespace("http://bigg-project.eu/ontology#")
ALL_QUERY = """SELECT DISTINCT ?s WHERE{ ?s ?p ?o}"""
COUNTRIES = {
    # "ES": {
    #     "file": "/Users/eloigabal/Downloads/ES/all-geonames-rdf-clean-ES.txt",
    #     "adms": [
    #         ("regions", "A.ADM1", None),
    #         ("province", "A.ADM2", "AddressProvince"),
    #         ("municipality", "A.ADM3", "AddressCity"),
    #     ]
    # },
    # "BG": {
    #     "file": "/Users/eloigabal/Downloads/ES/all-geonames-rdf-clean-BG.txt",
    #     "adms":[
    #         ("province", "A.ADM1", "AddressProvince"),
    #         ("municipality", "A.ADM2", "AddressCity")
    #     ]
    # },
    "GR": {
        "file": "/Users/francesc/Downloads/all-geonames-rdf-clean-GR.txt",
        "adms": [
            ("province", "A.ADM1", "AddressProvince"),
            ("municipality", "A.ADM3", "AddressCity")
        ]
    },
    # "CZ": {
    #     "file": "/Users/eloigabal/Downloads/ES/all-geonames-rdf-clean-CZ.txt",
    #     "adms": [
    #         ("province", "A.ADM1", "AddressProvince"),
    #         ("municipality", "A.ADM3", "AddressCity")
    #     ]
    # },
}


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
        rdf = requests.get(
            f"http://api.geonames.org/search?q={c}&featureCode=PCLI&maxRows=10&fuzzy=0.8&type=rdf&username=beegroup").content
        one_country = rdflib.Graph()
        one_country.parse(rdf)
        one_country = align_to_bigg(one_country, ALL_QUERY, [BIGG['AddressCountry']])
        all_countries += one_country
    all_countries.serialize("utils/rdf_utils/ontology/dictionaries/countries.ttl", format="ttl")


def create_graph(all_regions, type_adm):
    regions = rdflib.Graph()
    for result in all_regions.query(f"""SELECT ?s ?p ?o WHERE {{?s ?p ?o . ?s geo:featureCode geos:{type_adm}}}"""):
        regions.add(result)
    return regions


def save_rdf(g, f, format="ttl"):
    g1 = rdflib.Graph()
    try:
        g1.parse(f, format=format)
    except:
        pass
    g1 += g
    g1.serialize(f, format=format)


def get_adm_rdf(rdf_geonames_file, country_code, adms):
    all_regions = rdflib.Graph()
    #load geonames with https
    geos = Namespace("https://www.geonames.org/ontology#")
    geo = Namespace("http://www.geonames.org/ontology#")
    all_regions.namespace_manager.bind("bigg", BIGG)
    all_regions.namespace_manager.bind("geos", geos)
    all_regions.namespace_manager.bind("geo", geo)
    all_regions.parse(rdf_geonames_file, format="xml")
    for adm_type, adm_id, bigg_class in adms:
        adm_values = create_graph(all_regions, adm_id)
        if bigg_class:
            adm_values = align_to_bigg(adm_values, ALL_QUERY, [BIGG[bigg_class]])
        save_rdf(adm_values, f"utils/rdf_utils/ontology/dictionaries/{adm_type}_{country_code}.ttl", format="ttl")


def align_qudt(qudt_file):
    units = rdflib.Graph()
    units.namespace_manager.bind("bigg", BIGG)
    units.namespace_manager.bind("qudt", Namespace("http://qudt.org/schema/qudt/"))
    units.namespace_manager.bind("quantitykind", Namespace("http://qudt.org/vocab/quantitykind/"))
    units.parse(qudt_file, format="ttl")
    # EnergyEfficiencyMeasureInvestmentCurrency, ProjectInvestmentCurrency
    c_query = """SELECT DISTINCT ?s WHERE{ ?s qudt:hasQuantityKind quantitykind:Currency}"""
    units = align_to_bigg(units, c_query,
                          [BIGG['EnergyEfficiencyMeasureInvestmentCurrency'], BIGG['ProjectInvestmentCurrency'],
                           BIGG['TariffCurrency']])
    # AreaUnits
    a_query = """SELECT DISTINCT ?s WHERE{ ?s qudt:hasQuantityKind quantitykind:Area}"""
    units = align_to_bigg(units, a_query, [BIGG['AreaUnitOfMeasurement']])
    # MeasurementUnit
    units = align_to_bigg(units, ALL_QUERY, [BIGG['MeasurementUnit']])
    units.serialize("utils/rdf_utils/ontology/dictionaries/units.ttl", format="ttl")


if __name__ == "__main__":
    if sys.argv[1] == "countries":
        get_countries_rdf()
    elif sys.argv[1] == "regions":
        for cn, info in COUNTRIES.items():
            print(cn)
            get_adm_rdf(info['file'], cn, info['adms'])
    elif sys.argv[1] == "units":
        align_qudt("/Users/eloigabal/Downloads/qudtUnits.ttl")
    else:
        raise Exception("Choose a correct type")
