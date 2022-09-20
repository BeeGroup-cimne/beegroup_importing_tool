import os
import argparse
from functools import partial

import pandas as pd
from neo4j import GraphDatabase
from slugify import slugify

import settings
from utils.data_transformations import tariff_subject
from utils.neo4j import create_tariff
from utils.security import encrypt
from utils.utils import read_config

bigg = settings.namespace_mappings['bigg']

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create simpleTariff tariff.')
    main_org_params = parser.add_argument_group("Organization",
                                                "Set the main organization information for importing the data")
    main_org_params.add_argument("-u", "--user", help="The user that will import this data sources", required=True)
    main_org_params.add_argument("--namespace", "-n", help="The subjects namespace uri", required=True)
    main_org_params.add_argument("--tariff_name", "-name", help="The name of the new tariff", required=True)
    main_org_params.add_argument("--datasource", "-d", help="The datasource to link the tariff ", required=True)

    config = read_config(settings.conf_file)
    # get namespaces
    if os.getenv("PYCHARM_HOSTED"):
        args_t = ["-name", "endesa 2.1", "-n", "https://icaen.cat#", "-u", "icaen", "-d", "GemwebSource"]
        args = parser.parse_args(args_t)
    else:
        args = parser.parse_args()
    neo = GraphDatabase.driver(**config['neo4j'])
    with neo.session() as s:
        tariff_dict = {
            "tariffName": 'defined',
            "tariffCompany": 'CIMNE',
            'uri': f"{args.namespace}{tariff_subject('SimpleTariffSource', args.user, slugify(args.tariff_name))}"
        }
        create_tariff(s, tariff_dict, args.datasource, settings.namespace_mappings)

