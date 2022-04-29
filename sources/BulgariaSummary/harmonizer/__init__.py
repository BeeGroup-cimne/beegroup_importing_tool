from datetime import timedelta

import pandas as pd
from rdflib import Namespace

from sources.BulgariaSummary.harmonizer.Mapper import Mapper
from utils.rdf_utils.rdf_functions import generate_rdf


def harmonize_command_line():
    pass


def set_taxonomy(df):
    df['type_of_building'] = df['type_of_building'].str.strip()
    tax_df = pd.read_excel("data/tax/TAX_BULGARIA.xlsx", header=None, names=["Source", "Taxonomy"], sheet_name='Hoja1')
    tax_dict = {}
    for i in tax_df.to_dict(orient="records"):
        tax_dict.update({i['Source']: i['Taxonomy']})

    df['type_of_building'] = df['type_of_building'].map(tax_dict)
    return df


def set_country(df):
    pass


def harmonize_data(data, **kwargs):
    namespace = kwargs['namespace']
    user = kwargs['user']
    n = Namespace(namespace)
    config = kwargs['config']
    mapper = Mapper(config['source'], n)

    df = set_taxonomy(pd.DataFrame().from_records(data))

    df['subject'] = df['filename'] + '~' + df['id'].astype(str)
    df['building_name'] = df['subject'] + '~' + df['municipality'] + '~' + df['type_of_building']
    df['epc_date_before'] = df['epc_date'] - timedelta(days=365)
    df['epc_subject_before'] = df['subject'] + '~' + df['epc_energy_class_before']
    df['epc_subject_after'] = df['subject'] + '~' + df['epc_energy_class_after']
    g = generate_rdf(mapper.get_mappings("all"), df)
    print(g.serialize(format="ttl"))
    # save_rdf_with_source(g, config['source'], config['neo4j'])
