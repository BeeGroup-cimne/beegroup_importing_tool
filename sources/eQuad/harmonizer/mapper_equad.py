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


def calc_project_investment(row):
    # Present Project Cost
    engineeringAndDesignCosts = pd.DataFrame(row.get('engineeringAndDesignCosts'))['amount'].sum() if row.get(
        'engineeringAndDesignCosts') else 0

    equipmentCosts = pd.DataFrame(row.get('equipmentCosts'))['amount'].sum() if row.get('equipmentCosts') else 0

    installationAndConstructionCosts = pd.DataFrame(row.get('installationAndConstructionCosts'))[
        'amount'].sum() if row.get(
        'installationAndConstructionCosts') else 0

    salesAndBusinessDevelopmentCosts = pd.DataFrame(row.get('salesAndBusinessDevelopmentCosts'))[
        'amount'].sum() if row.get(
        'salesAndBusinessDevelopmentCosts') else 0

    legalAndInsuranceCosts = pd.DataFrame(row.get('legalAndInsuranceCosts'))['amount'].sum() if row.get(
        'legalAndInsuranceCosts') else 0

    otherCosts = pd.DataFrame(row.get('otherCosts'))['amount'].sum() if row.get('otherCosts') else 0

    markupCost = row.get('markupCost') if row.get('markupCost') else 0

    calc_present_project_cost = engineeringAndDesignCosts + equipmentCosts + installationAndConstructionCosts + salesAndBusinessDevelopmentCosts + legalAndInsuranceCosts + otherCosts + markupCost

    # Future Project Cost

    calc_future_project_cost = pd.DataFrame(row.get('oneOffCosts'))['amount'].sum() if row.get('oneOffCosts') else 0
    customer_down_payment = row.get('customerDownpayment') if row.get('customerDownpayment') else 0

    return calc_present_project_cost + calc_future_project_cost + customer_down_payment


def general_data(data):
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

    df['projectInvestment'] = df.apply(lambda x: calc_project_investment(x), axis=1)

    df['projectReceivedGrantFunding'] = df['incentives'].apply(lambda x: calc_investment(x) > 0)
    df['projectGrantsShareOfCosts'] = df['incentives'].apply(calc_investment)

    df['currencyCode'] = list(df['projectCurrency'].apply(lambda x: x['currencyCode']))
    unique_code = list(df['currencyCode'].unique())
    currency_map = fuzz_data(load_dic(["utils/rdf_utils/ontology/dictionaries/units.ttl"]), ['qudt:expression'],
                             unique_code)
    df['hasProjectInvestmentCurrency'] = df['currencyCode'].map(currency_map)

    df['tariffAveragePrice'] = df['sites'].apply(lambda x: calc_tarriff_avg(x))

    # Energy Efficiency Measure
    list_eem = []
    for index, row in df.iterrows():
        print(row.get('engineeringAndDesignCosts'))
        # OPEX = row['totalAuditCosts'] + row['totalEquipmentCost'] + row['totalInstallationCost'] + row[
        #     'totalConstructionCost'] * (1 + row['markupCost'] / 100)
        # CAPEX = 0
        # eem_investment = OPEX + CAPEX
        for site in row['sites']:
            for ecms in site.get('ecms'):
                list_eem.append({"_id": "",
                                 "energyEfficiencyMeasureDescription": ecms.get('descriptionNew'),
                                 "energyEfficiencyMeasureInvestmentCurrency": row['hasProjectInvestmentCurrency'],
                                 "energyEfficiencyMeasureOperationalDate": row['operationStartDate'],
                                 "energyEfficiencyMeasureType": ecms.get('typeOfMeasure'),
                                 "energyEfficiencyMeasureCO2Reduction": ecms.get('tCO2').get('amount'),
                                 "energyEfficiencyMeasureFinancialSavings": ecms.get('demandSavings').get(
                                     'amount') + ecms.get(
                                     'sellingSavings').get('amount') + ecms.get('consumptionSavings').get('amount'),
                                 "energyEfficiencyMeasureLifetime": ecms.get('usefulLife'),
                                 "energySavingEndDate": row['operationEndDate'],
                                 "energySavingStartDate": row['operationStartDate'],
                                 "energySavingType": ecms.get('category')
                                 }
                                )

    # TODO: energyEfficiencyMeasureType and energySavingType taxonomy

    print(list_eem)

    return df


def harmonize_data(data, **kwargs):
    namespace = kwargs['namespace']
    config = kwargs['config']
    n = Namespace(namespace)

    neo4j_connection = config['neo4j']
    neo = GraphDatabase.driver(**neo4j_connection)

    df = general_data(data)

    # if not df.empty:
    #     mapper = Mapper(config['source'], n)
    #     g = generate_rdf(mapper.get_mappings("all"), df)
    #
    #     g.serialize('output.ttl', format="ttl")
    #
    #     save_rdf_with_source(g, config['source'], config['neo4j'])
