import argparse
import os
import re
from datetime import datetime

import numpy as np
import pandas as pd

import utils
from harmonizer.cache import Cache


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
    # TODO: set date init and date end
    hbase_conn = config['ixon_raw_data']
    hbase_table = f"ixon_data_infraestructures"
    stop_date = str(datetime(day=20, month=6, year=2022, hour=0, second=0, minute=0).timestamp())

    Cache.load_cache()
    # Gather Raw Data from HBASE
    for data in utils.hbase.get_hbase_data_batch(hbase_conn, hbase_table, batch_size=1000,
                                                 row_start='C0:D3:91:31:E9:B1 - 17087108', reverse=True):

        dic_list = []
        for key, values in data:
            item = dict({'hbase_key': key.decode()})
            for key1, value1 in values.items():
                k = re.sub("^info:|^v:", "", key1.decode())
                item.update({k: value1.decode()})
                if 'building_internal_id' in item.keys():
                    dic_list.append(item)
        save_data(data=dic_list, data_type='ts', row_keys='_id', column_map=[("info", "all")],
                  config=config, settings=settings, args=args)


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
