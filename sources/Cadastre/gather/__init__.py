import argparse

from utils.hbase import save_to_hbase
from utils.kafka import save_to_kafka
from utils.nomenclature import raw_nomenclature, RAW_MODE
from utils.utils import log_string


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
                                            user=args.user)

            save_to_hbase(data, h_table_name, config['hbase_store_raw_data'], column_map,
                          row_fields=row_keys)
        except Exception as e:
            log_string(f"Error saving datadis supplies to HBASE: {e}")
    else:
        log_string(f"store {config['store']} is not supported")


def gather_data(config, settings, args):
    pass


def gather(arguments, settings, config):
    ap = argparse.ArgumentParser(description='Gathering data from cadastre')
    ap.add_argument("-st", "--store", required=True, help="Where to store the data", choices=["kafka", "hbase"])
    ap.add_argument("-t", "--type", help="Type of data", choices=["inspires"], default='INSPIRE')
    ap.add_argument("--user", "-u", help="The user importing the data", required=True)
    ap.add_argument("--namespace", "-n", help="The subjects namespace uri", required=True)
    ap.add_argument("--file", "-f", help="File to gather data")

    args = ap.parse_args(arguments)

    if args.type == 'INSPIRE' and not args.file:
        ap.error('--type=INSPIRE can only be set when --file=<file_path>.')

    gather_data(config=config, settings=settings, args=args)
