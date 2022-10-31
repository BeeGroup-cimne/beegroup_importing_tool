import os.path
import os
import sys
from neo4j import GraphDatabase
from utils.utils import read_config
import settings
import pandas as pd
import openpyxl

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
        if not os.path.exists(f"{trans_folder}/to_translate/"):
            os.makedirs(f"{trans_folder}/to_translate/")
        df.to_excel(f"{trans_folder}/to_translate/{t}_translations.xlsx", index=False)

def create_translation_files():
    make_english()
    make_trans_excel()

# import translations from file
def import_trans_excel(excel_file, field="rdfs__label"):
    df = pd.read_excel(excel_file)
    df.set_index("uri", inplace=True)
    for x, v in df.iterrows():
        value_trans = []
        for s, k in v.items():
            value_trans.append(f"{k}@{s}")
        with neo.session() as session:
            session.run(f"""Match (n{{uri:"{x}"}}) set n.{field}={value_trans}""")
            print(f"""Match (n{{uri:"{x}"}}) set n.{field}={value_trans}""")


# upload translations to neo4j

def upload_translations():
    for f in type_d:
        if os.path.exists(f"{trans_folder}/{f}_translations.xls"):
            import_trans_excel(f"{trans_folder}/{f}_translations.xls", "rdfs__label")
        if os.path.exists(f"{trans_folder}/{f}_tcomments.xls"):
            import_trans_excel(f"{trans_folder}/{f}_tcomments.xls", "rdfs__comment")


if __name__ == "__main__":
    if sys.argv[1] == "create":
        create_translation_files()
    elif sys.argv[1] == "translate":
        upload_translations()
    else:
        raise Exception("Valid options are 'create' and 'translate'")
