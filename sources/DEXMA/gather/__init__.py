import argparse

from dexma.device import Device

from utils.hbase import save_to_hbase
from utils.kafka import save_to_kafka
from utils.nomenclature import raw_nomenclature, RAW_MODE
from utils.utils import log_string


def gather_devices(config, settings, args):
    d = Device()
    count = 0
    limit = 500

    while True:
        res = d.get_devices({"start": limit * count, "limit": limit})

        try:
            assert res.status_code == 200
        except Exception as ex:
            log_string(f"{ex}", mongo=False)
            continue

        save_data(data=res.json(), data_type='Devices',
                  row_keys=['id'], column_map=[("info", "all")],
                  config=config, settings=settings, args=args, raw_mode=RAW_MODE.STATIC)

        if len(res.json()) == limit:
            count += 1
        else:
            break


def save_data(data, data_type, row_keys, column_map, config, settings, args, raw_mode):
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
            h_table_name = raw_nomenclature(source=config['source'], mode=raw_mode, data_type=data_type,
                                            user=args.user)

            save_to_hbase(data, h_table_name, config['hbase_store_raw_data'], column_map,
                          row_fields=row_keys)
        except Exception as e:
            log_string(f"Error saving datadis supplies to HBASE: {e}")
    else:
        log_string(f"store {config['store']} is not supported")


def gather(arguments, settings, config):
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", "-u", help="The user importing the data", required=True)
    ap.add_argument("--namespace", "-n", help="The subjects namespace uri", required=True)
    ap.add_argument("-st", "--store", required=True, help="Where to store the data", choices=["kafka", "hbase"])

    ap.add_argument("-k", "--kind_of_data", required=True, help="Where to store the data",
                    choices=["devices", "location", "parameter", "supplies", "reading", "all"])
    args = ap.parse_args(arguments)

    if args.kind_of_data == "devices" or args.kind_of_data == "all":
        gather_devices(arguments, settings, config)
