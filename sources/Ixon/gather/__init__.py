import argparse
import re

import utils
from harmonizer.cache import Cache


def gather_devices(config, settings, args):
    # todo: read excel that contain the devices
    # todo: save_data raw data
    pass


def gather_ts(config, settings, args):
    hbase_conn = config['ixon_raw_data']
    hbase_table = f"ixon_data_infraestructures"

    Cache.load_cache()

    for data in utils.hbase.get_hbase_data_batch(hbase_conn, hbase_table, batch_size=1000):
        dic_list = []
        for key, values in data:
            item = dict({'hbase_key': key.decode()})
            for key1, value1 in values.items():
                k = re.sub("^info:|^v:", "", key1.decode())
                item.update({k: value1.decode()})
            dic_list.append(item)
        save_data(dic_list, 'ts', '_id', config, settings, args)


def save_data(data, data_type, row_keys, config, settings, args):
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
            utils.kafka.save_to_kafka(topic=k_topic, info_document=kafka_message,
                                      config=config['kafka']['connection'], batch=settings.kafka_message_size)

        except Exception as e:
            utils.utils.log_string(f"error when sending message: {e}")


def gather(arguments, config=None, settings=None):
    ap = argparse.ArgumentParser(description='Gathering data from Nedgia')
    ap.add_argument("-st", "--store", required=True, help="Where to store the data", choices=["kafka", "hbase"])
    ap.add_argument("--user", "-u", help="The user importing the data", required=True)
    ap.add_argument("--type", "-t", help="Gather data", choices=['devices', 'ts'], required=True)
    ap.add_argument("--namespace", "-n", help="The subjects namespace uri", required=True)
    ap.add_argument("-f", "--file", required=True, help="Excel file path to parse")
    ap.add_argument("-so", "--source", required=True, help="The source importing the data")
    args = ap.parse_args(arguments)

    if args.type == 'devices':
        gather_devices(config=config, settings=settings, args=args)
    elif args.type == 'ts':
        gather_ts(config=config, settings=settings, args=args)
