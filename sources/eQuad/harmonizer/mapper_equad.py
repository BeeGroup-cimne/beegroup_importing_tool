from statistics import mean

import pandas as pd
from neo4j import GraphDatabase
from rdflib import Namespace

from utils.data_transformations import project_subject, fuzz_data, load_dic, decode_hbase, building_department_subject, \
    location_info_subject, building_subject, building_space_subject


def calc_investment(data) -> float:
    value = 0
    for i in data:
        if i.get('values'):
            value += sum(i.get('values'))

    return value


def calc_tarriff_avg(data):
    values = []
    for i in data:
        if i.get('tariffs'):
            for j in i.get('tariffs'):
                values.append(j.get('cost'))

    return mean(values) if values else None


def clean_data(data):
    df = pd.DataFrame(data)
    df = df.applymap(decode_hbase)

    # Organization
    df['organization_subject'] = df['customer'].apply(
        lambda x: building_department_subject(f"eQuad-{x.get('companyName')}") if isinstance(x, dict) else None)
    df['organizationEmail'] = df['customer'].apply(lambda x: x.get('email') if isinstance(x, dict) else None)
    df['organizationTelephoneNumber'] = df['customer'].apply(lambda x: x.get('phone') if isinstance(x, dict) else None)
    df['organizationName'] = df['customer'].apply(lambda x: x.get('companyName') if isinstance(x, dict) else None)

    # Building
    df['building_subject'] = df['_id'].apply(building_subject)

    # Building Space
    df['building_subject'] = df['_id'].apply(building_space_subject)

    # Location
    df['location_subject'] = df['_id'].apply(location_info_subject)
    df['addressPostalCode'] = df['customer'].apply(lambda x: x.get('customerZipCode') if isinstance(x, dict) else None)

    country_map = fuzz_data(load_dic(["utils/rdf_utils/ontology/dictionaries/countries.ttl"]), ['ns1:officialName'],
                            list(df['projectCountry'].unique()))

    df['addressCountry'] = df['projectCountry'].map(country_map)
    df['addressCountry'] = df['projectCountry'].map(country_map)

    # TODO: Change dictionary with all cities
    # df['city'] = df['customer'].apply(lambda x: x.get('customerCity') if isinstance(x, dict) else None)
    #
    #
    # city_map = fuzz_data(load_dic(["utils/rdf_utils/ontology/dictionaries/countries.ttl"]), ['ns1:officialName'],
    #                      list(df['projectCountry'].unique()))
    #
    # df['addressCity'] = df['city'].map(city_map)

    # Project
    df['project_subject'] = df['_id'].apply(project_subject)
    df.rename(columns={"description": "projectDescription", "name": "projectTitle",
                       "invesmentReturnRate": "projectDiscountRate", "inflation": "projectInterestRate",
                       "irr": "projectInternalRateOfReturn", "npv": "projectNetPresentValue",
                       "operationStartDate": "projectOperationalDate", "payback": "projectSimplePaybackTime",
                       "installationBeginDate": "projectStartDate"}, inplace=True)

    # projectInvestment

    df['projectReceivedGrantFunding'] = df['incentives'].apply(lambda x: calc_investment(x) > 0)
    df['projectGrantsShareOfCosts'] = df['incentives'].apply(calc_investment)

    df['currencyCode'] = list(df['projectCurrency'].apply(lambda x: x['currencyCode']))
    unique_code = list(df['currencyCode'].unique())
    currency_map = fuzz_data(load_dic(["utils/rdf_utils/ontology/dictionaries/units.ttl"]), ['qudt:expression'],
                             unique_code)
    df['hasProjectInvestmentCurrency'] = df['currencyCode'].map(currency_map)

    df['tariffAveragePrice'] = df['sites'].apply(lambda x: calc_tarriff_avg(x))


    return df


def harmonize_data(data, **kwargs):
    namespace = kwargs['namespace']
    config = kwargs['config']
    n = Namespace(namespace)

    neo4j_connection = config['neo4j']
    neo = GraphDatabase.driver(**neo4j_connection)

    df = clean_data(data, n, neo)

    # if not df.empty:
    #     mapper = Mapper(config['source'], n)
    #     g = generate_rdf(mapper.get_mappings("all"), df)
    #
    #     g.serialize('output.ttl', format="ttl")
    #
    #     save_rdf_with_source(g, config['source'], config['neo4j'])
