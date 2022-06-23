import argparse
import os

import numpy as np
import pandas as pd

import utils
from utils.hdfs import generate_input_tsv
from utils.mongo import mongo_connection


def gather_devices(config, settings, args):
    for file in os.listdir(f"data/{config['source']}"):
        if file.endswith('.xlsx'):
            df = pd.read_excel(f"data/{config['source']}/{file}")
            df['Object ID'] = df['Object ID'].fillna(0).astype(np.int64)
            df['Object ID'] = df['Object ID'].astype(str)
            save_data(data=df.to_dict(orient="records"), data_type='static',
                      row_keys=['Description', 'BACnet Type', 'Object ID'], column_map=[("info", "all")],
                      config=config, settings=settings, args=args)


def gather_ts(config, settings, args):
    # Connect to MongoDB
    db_ixon_users = mongo_connection(config['mongo_db'])['ixon_users']

    # Generate TSV File
    generate_input_tsv(db_ixon_users.find({}), ["email", "password", "api_application", "description"])


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
                "column_map": column_map,
                "data": data
            }
            utils.kafka.save_to_kafka(topic=k_topic, info_document=kafka_message,
                                      config=config['kafka']['connection'], batch=settings.kafka_message_size)

        except Exception as e:
            utils.utils.log_string(f"error when sending message: {e}")
    elif args.store == "hbase":
        try:
            h_table_name = f"{config['data_sources'][config['source']]['hbase_table']}_{data_type}_{args.type}__{args.user}"
            utils.hbase.save_to_hbase(data, h_table_name, config['hbase_store_raw_data'], column_map,
                                      row_fields=row_keys)
        except Exception as e:
            utils.utils.log_string(f"Error saving datadis supplies to HBASE: {e}")
    else:
        utils.utils.log_string(f"store {config['store']} is not supported")


def gather(arguments, config=None, settings=None):
    ap = argparse.ArgumentParser(description='Gathering data from Nedgia')
    ap.add_argument("-st", "--store", required=True, help="Where to store the data", choices=["kafka", "hbase"])
    ap.add_argument("--user", "-u", help="The user importing the data", required=True)
    ap.add_argument("--type", "-t", help="Gather data", choices=['devices', 'ts'], required=True)
    ap.add_argument("--namespace", "-n", help="The subjects namespace uri", required=True)
    ap.add_argument("-f", "--file", required=True, help="Excel file path to parse")
    args = ap.parse_args(arguments)

    if args.type == 'devices':
        gather_devices(config=config, settings=settings, args=args)
    elif args.type == 'ts':
        gather_ts(config=config, settings=settings, args=args)
