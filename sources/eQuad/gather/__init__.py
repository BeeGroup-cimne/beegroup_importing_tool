import argparse
from json import dumps

import requests

from utils.hbase import save_to_hbase
from utils.kafka import save_to_kafka
from utils.nomenclature import raw_nomenclature, RAW_MODE
from utils.utils import log_string

BASE_URL = "https://staging-c3po.equadcapital.com"
BASE_HEADERS = {'Content-Type': 'application/json;charset=utf-8'}


def get_token(**kwargs):
    return requests.post(f"{BASE_URL}/authenticate", headers=BASE_HEADERS,
                         data=dumps({"email": kwargs['username'], "password": kwargs['password']}))


def get_projects(token):
    return requests.get(f"{BASE_URL}/api/projects?token={token}")


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
            save_to_kafka(topic=k_topic, info_document=kafka_message,
                          config=config['kafka']['connection'], batch=settings.kafka_message_size)

        except Exception as e:
            log_string(f"error when sending message: {e}")

    elif args.store == "hbase":

        try:
            h_table_name = raw_nomenclature(mode=RAW_MODE.STATIC, data_type=data_type, frequency="", user=args.user,
                                            source=config['source'])
            save_to_hbase(data, h_table_name, config['hbase_store_raw_data'], column_map,
                          row_fields=row_keys)
        except Exception as e:
            log_string(f"Error saving datadis supplies to HBASE: {e}")
    else:
        log_string(f"store {config['store']} is not supported")


def gather(arguments, config=None, settings=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", "-u", help="The user importing the data", required=True)
    ap.add_argument("--namespace", "-n", help="The subjects namespace uri", required=True)
    ap.add_argument("-st", "--store", required=True, help="Where to store the data", choices=["kafka", "hbase"])
    args = ap.parse_args(arguments)

    response_token = get_token(**config['eQuad'])

    if response_token.ok:
        token = response_token.json()['token']
    else:
        raise response_token.raise_for_status()

    response_projects = get_projects(token=token)

    if response_projects.ok:
        save_data(data=response_projects.json(), data_type='Projects',
                  row_keys=['_id'], column_map=[("info", "all")],
                  config=config, settings=settings, args=args)
    else:
        raise response_projects.raise_for_status()
