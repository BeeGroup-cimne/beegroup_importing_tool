from statistics import mean

import pandas as pd
from neo4j import GraphDatabase
from rdflib import Namespace

from sources.eQuad.harmonizer.Mapper import Mapper
from utils.data_transformations import project_subject, fuzz_data, load_dic, building_department_subject, \
    location_info_subject, building_subject, building_space_subject, eem_subject, construction_element_subject, \
    energy_saving_subject
from utils.rdf_utils.rdf_functions import generate_rdf


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


def get_value(row, column, target, default_value=0) -> pd.DataFrame:
    return pd.DataFrame(row.get(column))[target].sum() if row.get(column) else default_value


def calc_project_investment(row):
    # Present Project Cost
    engineeringAndDesignCosts = get_value(row=row, column='engineeringAndDesignCosts', target='amount')

    equipmentCosts = get_value(row=row, column='equipmentCosts', target='amount')

    installationAndConstructionCosts = get_value(row=row, column='installationAndConstructionCosts', target='amount')

    salesAndBusinessDevelopmentCosts = get_value(row=row, column='salesAndBusinessDevelopmentCosts', target='amount')

    legalAndInsuranceCosts = get_value(row=row, column='legalAndInsuranceCosts', target='amount')

    otherCosts = get_value(row=row, column='otherCosts', target='amount')

    markupCost = float(row.get('markupCost')) if row.get('markupCost') and not pd.isna(row.get('markupCost')) else 0

    calc_present_project_cost = engineeringAndDesignCosts + equipmentCosts + installationAndConstructionCosts + salesAndBusinessDevelopmentCosts + legalAndInsuranceCosts + otherCosts + markupCost

    # Future Project Cost

    calc_future_project_cost = get_value(row=row, column='oneOffCosts', target='amount')
    customer_down_payment = float(row.get('customerDownpayment')) if row.get(
        'customerDownpayment') and not pd.isna(row.get('customerDownpayment')) else 0

    return calc_present_project_cost + calc_future_project_cost + customer_down_payment


def general_data(data, n):
    df = pd.DataFrame(data)
    # df = df.applymap(decode_hbase)

    df['subject'] = df['_id']

    # Organization
    df['organization_subject'] = df['customer'].apply(
        lambda x: building_department_subject(f"eQuad-{x.get('companyName').replace(' ', '-')}") if isinstance(x,
                                                                                                               dict) else "eQuad-Undefined")
    df['organizationEmail'] = df['customer'].apply(lambda x: x.get('email') if isinstance(x, dict) else None)
    df['organizationTelephoneNumber'] = df['customer'].apply(lambda x: x.get('phone') if isinstance(x, dict) else None)
    df['organizationName'] = df['customer'].apply(lambda x: x.get('companyName') if isinstance(x, dict) else None)

    # Building
    df['building_subject'] = df['_id'].apply(building_subject)
    df['managesBuilding'] = df['building_subject'].apply(lambda x: n[x])

    # Building Space
    df['building_space_subject'] = df['_id'].apply(building_space_subject)
    df['hasSpace'] = df['building_space_subject'].apply(lambda x: n[x])

    # Location
    df['location_subject'] = df['_id'].apply(location_info_subject)
    df['hasLocationInfo'] = df['location_subject'].apply(lambda x: n[x])
    df['addressPostalCode'] = df['customer'].apply(lambda x: x.get('customerZipCode') if isinstance(x, dict) else None)

    country_map = fuzz_data(load_dic(["utils/rdf_utils/ontology/dictionaries/countries.ttl"]), ['ns1:officialName'],
                            list(df['projectCountry'].unique()))

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
    df['hasProject'] = df['project_subject'].apply(lambda x: n[x])
    df.rename(columns={"description": "projectDescription", "name": "projectName",
                       "invesmentReturnRate": "projectDiscountRate", "inflation": "projectInterestRate",
                       "irr": "projectInternalRateOfReturn", "npv": "projectNetPresentValue",
                       "operationStartDate": "projectOperationalDate", "payback": "projectSimplePaybackTime",
                       "installationBeginDate": "projectStartDate"}, inplace=True)

    df['projectInvestment'] = df.apply(lambda x: calc_project_investment(x), axis=1)

    df['projectReceivedGrantFounding'] = df['incentives'].apply(lambda x: calc_investment(x) > 0)
    df['projectGrantsShareOfCosts'] = df['incentives'].apply(calc_investment)

    df['currencyCode'] = list(df['projectCurrency'].apply(lambda x: x['currencyCode']))
    unique_code = list(df['currencyCode'].unique())
    currency_map = fuzz_data(load_dic(["utils/rdf_utils/ontology/dictionaries/units.ttl"]), ['qudt:expression'],
                             unique_code)
    df['hasProjectInvestmentCurrency'] = df['currencyCode'].map(currency_map)

    df['tariffAveragePrice'] = df['sites'].apply(lambda x: calc_tarriff_avg(x))

    # Element
    df['element_subject'] = df['subject'].apply(construction_element_subject)
    df['element_uri'] = df['element_subject'].apply(lambda x: n[construction_element_subject])

    # Energy Efficiency Measure
    list_eem = []
    for index, row in df.iterrows():
        for site in row['sites']:
            for ecms in site.get('ecms'):
                list_eem.append(
                    {"eem_subject": eem_subject(f"{row.get('_id')}-{ecms.get('typeOfMeasure').replace(' ', '-')}"),
                     "energyEfficiencyMeasureDescription": ecms.get('descriptionNew'),
                     "energyEfficiencyMeasureInvestmentCurrency": row.get('hasProjectInvestmentCurrency'),
                     "energyEfficiencyMeasureOperationalDate": row.get('projectOperationalDate'),
                     "energyEfficiencyMeasureType": ecms.get('typeOfMeasure'),
                     "energyEfficiencyMeasureCO2Reduction": ecms.get('tCO2').get('amount'),
                     "energyEfficiencyMeasureFinancialSavings": ecms.get('demandSavings').get(
                         'amount') + ecms.get(
                         'sellingSavings').get('amount') + ecms.get('consumptionSavings').get('amount'),
                     "energyEfficiencyMeasureLifetime": ecms.get('usefulLife'),
                     "energySavingEndDate": row['operationEndDate'],
                     "energySavingStartDate": row['projectOperationalDate'],
                     "energySavingType": ecms.get('category'),
                     "energy_saving_subject": energy_saving_subject(row.get('_id')),
                     "producesSaving": n[energy_saving_subject(row.get('_id'))],
                     "affectsElement": ecms.get('element_uri')
                     }
                )

    # TODO: energyEfficiencyMeasureType and energySavingType taxonomy

    return df, pd.DataFrame(list_eem)


def harmonize_data(data, **kwargs):
    namespace = kwargs['namespace']
    config = kwargs['config']
    n = Namespace(namespace)

    neo4j_connection = config['neo4j']
    neo = GraphDatabase.driver(**neo4j_connection)

    df_general, df_eem = general_data(data, n)

    mapper = Mapper(config['source'], n)

    if not df_general.empty and not df_eem.empty:
        g = generate_rdf(mapper.get_mappings("project"), df_general)
        g.serialize('output.ttl', format="ttl")

        # save_rdf_with_source(g, config['source'], config['neo4j'])

        g = generate_rdf(mapper.get_mappings("eem"), df_eem)
        g.serialize('output2.ttl', format="ttl")

        # save_rdf_with_source(g, config['source'], config['neo4j'])
