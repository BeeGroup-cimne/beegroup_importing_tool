import os.path
import os
import sys

from neo4j import GraphDatabase
from utils.utils import read_config
import settings
import pandas as pd
config = read_config(settings.conf_file)
neo = GraphDatabase.driver(**config['neo4j'])
type_d = ["AreaType", "BuildingSpaceUseType", "EnergyEfficiencyMeasureType", "BuildingConstructionElementType",
          "DeviceType", "UtilityType"]

trans_folder = "translations"

def make_english():
    for t in type_d:
        with neo.session() as session:
            session.run(f"""
            Match(n: bigg__{t}) 
            SET n.rdfs__label = [
                apoc.text.regreplace(apoc.text.split(apoc.text.split(n.uri, "#")[1], "\.")[-1], "(.)([A-Z])", "$1 $2") + "@en"];
            """)

# first call make_english
def make_trans_excel():
    for t in type_d:
        with neo.session() as session:
            translation = session.run(f"""
            MATCH (n:bigg__{t}) RETURN n.uri as uri, split([s in n.rdfs__label where split(s,"@")[1]="en"][0],"@")[0] as en
            """).data()

        df = pd.DataFrame.from_records(translation)
        df.to_excel(f"{trans_folder}/{t}_translations.xls", index=False)

# import translations from file
def import_trans_excel(excel_file, field="rdfs__label"):
    df = pd.read_excel(excel_file)
    df.set_index("uri", inplace=True)
    for x, v in df.iterrows():
        with neo.session() as session:
            session.run(f"""Match (n{{uri:"{x}"}}) set n.{field}=[]""")
        for s, k in v.items():
            with neo.session() as session:
                session.run(f"""Match (n{{uri:"{x}"}}) set n.{field}=["{k}@{s}"] + n.{field}""")
                print(f"""Match (n{{uri:"{x}"}}) set n.{field}=["{k}@{s}"] + n.{field}""")


# upload translations to neo4j

def upload_translations():
    for f in type_d:
        if os.path.exists(f"{trans_folder}/{f}_translations.xls"):
            import_trans_excel(f"{trans_folder}/{f}_translations.xls", "rdfs__label")
        if os.path.exists(f"{trans_folder}/{f}_tcomments.xls"):
            import_trans_excel(f"{trans_folder}/{f}_tcomments.xls", "rdfs__comment")


if __name__ == "__main__":
    if sys.argv[1] == "create":
        make_english()
        make_trans_excel()
    elif sys.argv[1] == "translate":
        upload_translations()
    else:
        raise Exception("Valid options are 'create' and 'translate'")
