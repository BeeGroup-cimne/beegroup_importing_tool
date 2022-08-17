import argparse
from enum import Enum

import pandas as pd
from dexma.device import Device
from dexma.location import Location
from dexma.reading import Reading
from dexma.supply import Supply

from utils.hbase import save_to_hbase
from utils.kafka import save_to_kafka
from utils.nomenclature import raw_nomenclature
from utils.utils import log_string


class SupplyEnum(Enum):
    WATER = 'WATER',
    ELECTRICITY = 'ELECTRICITY'
    GAS = 'GAS'


def gather_static_data(config, settings, args):
    count = 0
    limit = 500

    while True:
        devices = Device().get_devices({"start": count * limit, "limit": limit}).json()

        for index, row in pd.DataFrame(devices).iterrows():
            if row['location']:
                location = gather_location(row['location']['id']).json()

        if len(devices) == limit:
            count += 1
        else:
            break


def gather_reads(device_id, date_init, date_end):
    try:
        r = Reading()
        res = r.get_readings_by_parameter_key({"device_id": device_id,
                                               "parameter_key": 'CURRENT',
                                               "operation": "RAW",
                                               "resolution": 'H',
                                               "from": date_init,
                                               "to": date_end})
        return res
    except Exception as ex:
        print(f"{ex}")


def gather_supplies(supply_type: SupplyEnum):
    limit = 20
    count = 0
    while True:
        supplies = Supply().get_energy_source_supplies(supply_type.value,
                                                       {"start": count * limit, "limit": limit}).json()

        if len(supplies) == limit:
            count += 1
        else:
            break


def gather_location(id):
    return Location().get_location(id)


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

    # if args.kind_of_data == "devices" or args.kind_of_data == "all":
    #     gather_devices(arguments, settings, config)
