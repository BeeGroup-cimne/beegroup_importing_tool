import os
import argparse
from functools import partial

import pandas as pd
from neo4j import GraphDatabase
from slugify import slugify

import settings
from utils.security import encrypt
from utils.utils import read_config

bigg = settings.namespace_mappings['bigg']

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Create Gemweb connections.')
    main_org_params = parser.add_argument_group("Organization",
                                                "Set the main organization information for importing the data")
    main_org_params.add_argument("-f", "--file", help="Import the organization from file", required=True)
    main_org_params.add_argument("-u", "--user", help="The user that will import this data sources", required=True)
    main_org_params.add_argument("--namespace", "-n", help="The subjects namespace uri", required=True)
    main_org_params.add_argument("--datasource", "-d", help="The datasource to create credentials", required=True)

    config = read_config(settings.conf_file)
    # get namespaces
    if os.getenv("PYCHARM_HOSTED"):
        args_t = ["-f", "data/DataSources/gemweb.xls", "-n", "https://icaen.cat#", "-u", "icaen", "-d", "GemwebSource"]
        args = parser.parse_args(args_t)
    else:
        args = parser.parse_args()

    neo = GraphDatabase.driver(**config['neo4j'])
    df = pd.read_excel(args.file)
    if 'Password' in df.columns:
        df['Password'] = df['Password'].apply(partial(encrypt, password=os.getenv(config['encrypt_pass']['environment'])))

    for c in df.columns:
        if c.startswith("_"):
            df.drop(c, axis=1, inplace=True)

    with neo.session() as s:
        for _, org in df.iterrows():
            uri = f"{args.namespace}{slugify(org.pop('Organization'))}"
            username = org.pop("Username") if "Username" in org.keys() else None
            new_line = "\n"
            res = s.run(
                f"""
                    MATCH (o1:{bigg}__Organization {{userID:"{args.user}"}})-
                          [:{bigg}__hasSubOrganization*0..]->(o:{bigg}__Organization {{uri:"{uri}"}})
                    Merge (x:{args.datasource} {f"{{username:'{username}'}}" if username else ""} )<-[:hasSource]-(o)
                    {new_line.join([f"SET x.{str(k)}='{str(v)}'" for k, v in org.items()])}
                    RETURN x
                """)


