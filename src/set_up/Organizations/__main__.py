import argparse
import os

from neo4j import GraphDatabase
from rdflib import Namespace, Graph
from slugify import slugify

import settings
import pandas as pd

from set_up.Organizations.organization_mapping import set_params, get_mappings
from ontology.namespaces_definition import *
from utils.rdf.rdf_functions import generate_rdf
from utils.rdf.save_rdf import save_rdf_with_source
from utils.utils import read_config

source = "Org"

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Mapping of Organization data to neo4j.')
    exec_settings = parser.add_argument_group("General", "General settings of the script")
    exec_settings.add_argument("-f", "--file", help="Import the organization from file", required=True)

    main_org_params = parser.add_argument_group("Organization",
                                                "Set the main organization information for importing the data")
    main_org_params.add_argument("--organization_name", "-name", help="The main organization name", required=True)
    main_org_params.add_argument("--user", "-u", help="The main organization name", required=True)
    main_org_params.add_argument("--namespace", "-n", help="The subjects namespace uri", required=True)
    if os.getenv("PYCHARM_HOSTED"):
        args_t = ["-f", "data/Organizations/organizations.xls", "-name", "Generalitat de Catalunya", "-n",
                  "https://icaen.cat#", "-u", "icaen"]
        args = parser.parse_args(args_t)
    else:
        args = parser.parse_args()
    # read config file
    config = read_config(settings.conf_file)
    # get namespaces
    bigg = settings.namespace_mappings['bigg']

    org_levels_df = []
    level = 0
    while True:
        try:
            org_levels_df.append(pd.read_excel(args.file, sheet_name=level))
            level += 1
        except (IndexError, ValueError):
            break

    n = Namespace(args.namespace)
    set_params(args.organization_name, source, n)

    print("mapping data")
    # generate main org

    g_levels = []
    for dfl in org_levels_df:
        g_levels.append(generate_rdf(get_mappings("level"), dfl))

    # Create links between graph
    total_g = Graph()
    for index, dfs in enumerate(org_levels_df):
        if index == 0:
            parent_df = None
        else:
            parent_df = org_levels_df[index - 1]
        total_g += g_levels[index]
        for x, row in dfs.iterrows():
            if parent_df is not None:
                r_parent = parent_df[parent_df.id == row.link]
                total_g.add((n[slugify(r_parent['name'].values[0])], Bigg.hasSubOrganization, n[slugify(row["name"])]))

    print("saving to node4j")
    save_rdf_with_source(total_g, source, config['neo4j'])
    # add userID to main organization
    neo4j = GraphDatabase.driver(**config['neo4j'])
    with neo4j.session() as session:
        dfs = org_levels_df[0]
        for _, org in dfs.iterrows():
            session.run(f"""
            MATCH (n:{bigg}__Organization{{uri:"{n[slugify(org['name'])]}"}}) 
            SET n.userID="{args.user}" 
            RETURN n""")
