import argparse
import os

import pandas as pd

from utils import nomenclature
from utils.hbase import save_to_hbase
from utils.kafka import save_to_kafka
from utils.nomenclature import RAW_MODE
from utils.utils import log_string

COLUMN_NAMES = ['Year', 'Month', 'Code', 'Municipality Unit', 'Municipality', 'Region', 'Office', 'Meter num',
                'Bill num', 'Bill num 2', 'Name', 'Street', 'Street num', 'City', 'Bill Issuing Day', 'Month1', 'Year1',
                'Meter Code', 'Type Of Billing', 'Current Record', 'Previous Record', 'Variable', 'Recording Date',
                'Previous Recording Date', 'Electricity Consumption', 'Electricity Cost', 'VAT', 'Other',
                'Prev payment',
                'Energy Value', 'VAT Prev Payment', 'EPT', 'Out service', 'Debit/Credit', 'ETMEAR', 'VAT ETMEAR',
                'Special TAX', 'TAX', 'Low VAT',
                'High VAT', 'Intermediate Value', 'Total Energy Value', 'Total VAT of electricity',
                'Total VAT Services', 'Total VAT', 'Total ERT', 'Municipal TAX', 'Total TAP',
                'EETIDE', 'Total Account', 'Total Current Month', 'Account Type',
                'Municipality Unit 1']


def gather_data(config, settings, args):
    for file in os.listdir(args.file):
        if file.endswith('.xlsx'):
            path = f"{args.file}/{file}"
            df = pd.read_excel(path,
                               skiprows=7, header=None, names=COLUMN_NAMES)
            df = df.dropna(axis=0, how='all')

            save_data(data=df.to_dict(orient='records'), data_type="BuildingInfo",
                      row_keys=["Year", "Month", 'Code'],
                      column_map=[("info", "all")], config=config, settings=settings, args=args)


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
            h_table_name = nomenclature.raw_nomenclature(config['source'], RAW_MODE.STATIC, data_type=data_type,
                                                         frequency="", user=args.user)

            save_to_hbase(data, h_table_name, config['hbase_store_raw_data'], column_map,
                          row_fields=row_keys)
        except Exception as e:
            log_string(f"Error saving datadis supplies to HBASE: {e}")
    else:
        log_string(f"store {config['store']} is not supported")


def gather(arguments, config=None, settings=None):
    ap = argparse.ArgumentParser(description='Gathering data from ePlanet')
    ap.add_argument("-st", "--store", required=True, help="Where to store the data", choices=["kafka", "hbase"])
    ap.add_argument("--user", "-u", help="The user importing the data", required=True)
    ap.add_argument("--namespace", "-n", help="The subjects namespace uri", required=True)
    ap.add_argument("-f", "--file", required=True, help="Excel file path to parse")
    args = ap.parse_args(arguments)

    gather_data(config=config, settings=settings, args=args)
