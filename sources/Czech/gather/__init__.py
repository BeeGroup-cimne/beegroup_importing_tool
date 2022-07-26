import argparse

import pandas as pd

from utils.hbase import save_to_hbase
from utils.kafka import save_to_kafka
from utils.nomenclature import raw_nomenclature, RAW_MODE
from utils.utils import log_string

COLUMNS_BUILDINGS = ['ID', 'Country', 'Region', 'Municipality', 'Road', 'Road Number', 'PostalCode', 'Longitude',
                     'Latitude', 'Name', 'Use Type', 'Owner', 'YearOfConstruction', 'GrossFloorArea', 'Renewable',
                     'EnergyAudit', 'Monitoring', 'SolarPV', 'SolarThermal', 'SolarThermalPower', 'EnergyCertificate',
                     'EnergyCertificateDate', 'EnergyCertificateQualification', 'HeatingSource',
                     'OriginalInstalledPower', 'OriginalInstalledPowerAfter']


def save_data(data, data_type, row_keys, column_map, config, settings, args):
    if args.store == "kafka":
        try:
            k_topic = config["kafka"]["topic"]
            kafka_message = {
                "namespace": args.namespace,
                "user": args.user,
                "collection_type": data_type,
                "source": config['source'],
                "row_keys": row_keys,
                "data": data
            }
            save_to_kafka(topic=k_topic, info_document=kafka_message,
                          config=config['kafka']['connection'], batch=settings.kafka_message_size)

        except Exception as e:
            log_string(f"error when sending message: {e}")

    elif args.store == "hbase":

        try:
            h_table_name = raw_nomenclature(source=config['source'], mode=RAW_MODE.STATIC, data_type=data_type,
                                            frequency="", user=args.user)

            save_to_hbase(data, h_table_name, config['hbase_store_raw_data'], column_map,
                          row_fields=row_keys)
        except Exception as e:
            log_string(f"Error saving datadis supplies to HBASE: {e}")
    else:
        log_string(f"store {config['store']} is not supported")


def gather(arguments, settings, config):
    ap = argparse.ArgumentParser(description='Gathering data from Czech')
    ap.add_argument("-st", "--store", required=True, help="Where to store the data", choices=["kafka", "hbase"])
    ap.add_argument("--user", "-u", help="The user importing the data", required=True)
    ap.add_argument("--namespace", "-n", help="The subjects namespace uri", required=True)
    ap.add_argument("-f", "--file", required=True, help="Excel file path to parse")
    ap.add_argument("-kf", "--kind_of_file", required=True,
                    help="Choice the kind of file that you would like to harmonize.",
                    choices=['region', 'municipality', 'building_data', 'building_eem'])
    args = ap.parse_args(arguments)

    if args.kinf_of_file == 'building_data':
        df = pd.read_excel(args.file, skiprows=1, sheet_name=0)
        df = df.rename(columns={"Unikátní kód": 'Unique ID'}, inplace=True)

        save_data(data=df.to_dict(orient="records"), data_type="BuildingInfo",
                  row_keys=["Unique ID"],
                  column_map=[("info", "all")], config=config, settings=settings, args=arguments)

    if args.kinf_of_file == 'building_eem':
        df = pd.read_excel(args.file, skiprows=1, sheet_name=1)
        df.rename(columns={"Unikátní kód": 'Unique ID'}, inplace=True)

        save_data(data=df.to_dict(orient="records"), data_type="EnergyEfficiencyMeasure",
                  row_keys=["Unique ID"],
                  column_map=[("info", "all")], config=config, settings=settings, args=arguments)

    if args.kinf_of_file == 'municipality':
        df = pd.read_excel(args.files, skiprows=5)
        df.dropna(how='all', axis='columns', inplace=True)
        unique_id = args.files.split('/')[-1].split['_'][0]
        df['Unique ID'] = unique_id
        save_data(data=df.to_dict(orient="records"), data_type="municipality_ts",
                  row_keys=["Unique ID"],
                  column_map=[("info", "all")], config=config, settings=settings, args=arguments)

    if args.kinf_of_file == 'region':
        df = pd.read_excel(args.files, sheet_name='souhrn', skiprows=100)
        df.dropna(how='all', axis='columns')

        df['Unique ID'] = args.files.split('/')[-1]
        save_data(data=df.to_dict(orient="records"), data_type="region_ts",
                  row_keys=["Unique ID"],
                  column_map=[("info", "all")], config=config, settings=settings, args=arguments)
