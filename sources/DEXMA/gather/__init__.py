import argparse
from enum import Enum

import pandas as pd
from dateutil.parser import parse
from dexma.device import Device
from dexma.location import Location
from dexma.reading import Reading
from dexma.supply import Supply

from utils.hbase import save_to_hbase
from utils.kafka import save_to_kafka
from utils.nomenclature import raw_nomenclature, RAW_MODE
from utils.utils import log_string


class SupplyEnum(Enum):
    WATER = 'WATER',
    ELECTRICITY = 'ELECTRICITY'
    GAS = 'GAS'


def gather_locations(args, settings, config):
    count = 0
    limit = 500

    list_locations = []

    while True:
        locations = Location().get_locations({"start": count * limit, "limit": limit}).json()
        list_locations += locations
        save_data(data=locations, data_type='Locations',
                  row_keys=['id'], column_map=[("info", "all")],
                  config=config, settings=settings, args=args, raw_mode=RAW_MODE.STATIC)

        if len(locations) == limit:
            count += 1
        else:
            break

    return list_locations


def gather_devices(locations, args, settings, config):
    count = 0
    limit = 500

    while True:
        devices = Device().get_devices({"start": count * limit, "limit": limit}).json()
        if len(devices) == limit:
            count += 1
        else:
            break

        # Save Raw Data
        save_data(data=devices, data_type='Devices',
                  row_keys=['id'], column_map=[("info", "all")],
                  config=config, settings=settings, args=args, raw_mode=RAW_MODE.STATIC)

        # To Harmonize
        df_loc = pd.json_normalize(locations, sep='_')
        df_loc['id'] = df_loc['id'].astype(float)

        df_dev = pd.json_normalize(devices, sep='_')

        df_dev_none = df_dev[df_dev['location_id'].isnull()].copy()
        save_data(data=df_dev_none.to_dict(orient='records'), data_type='Devices-None',
                  row_keys=['id'], column_map=[("info", "all")],
                  config=config, settings=settings, args=args, raw_mode=RAW_MODE.STATIC)

        df_dev_full = df_dev[df_dev['location_id'].notnull()].copy()

        df_joined = pd.merge(df_loc, df_dev_full, left_on=['id'], right_on=['location_id'])

        save_data(data=df_joined.to_dict(orient='records'), data_type='Devices-Joined',
                  row_keys=['id'], column_map=[("info", "all")],
                  config=config, settings=settings, args=args, raw_mode=RAW_MODE.STATIC)

        if len(devices) == limit:
            count += 1
        else:
            break


def gather_reads(args, settings, config):
    count = 0
    limit = 500

    while True:
        res = Device().get_devices({"start": count * limit, "limit": limit})

        devices = res.json()

        for device in devices:
            try:
                r = Reading()
                res = r.get_readings_by_parameter_key({"device_id": device['id'],
                                                       "parameter_key": 'CURRENT',
                                                       "operation": "RAW",
                                                       "resolution": 'H',
                                                       "from": parse(args.date_init).isoformat(),
                                                       "to": parse(args.date_end).isoformat()})
                df = pd.DataFrame([res.json()])

                df[
                    'id'] = f"{device['id']}~{int(parse(args.date_init).timestamp())}~{int(parse(args.date_end).timestamp())}"

                save_data(data=df.to_dict(orient='records'), data_type='TimeSeries',
                          row_keys=['id'], column_map=[("info", "all")],
                          config=config, settings=settings, args=args, raw_mode=RAW_MODE.TIMESERIES)
            except Exception as ex:
                print(f"{ex}")

        if len(devices) == limit:
            count += 1
        else:
            break


def gather_supplies(args, settings, config, supply_type: SupplyEnum):
    limit = 500
    count = 0
    while True:
        supplies = Supply().get_energy_source_supplies(supply_type.value,
                                                       {"start": count * limit, "limit": limit}).json()

        save_data(data=supplies, data_type='Supplies',
                  row_keys=['id'], column_map=[("info", "all")],
                  config=config, settings=settings, args=args, raw_mode=RAW_MODE.STATIC)

        if len(supplies) == limit:
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

    ap.add_argument("-di", "--date_init", help="Where to store the data", choices=["kafka", "hbase"])
    ap.add_argument("-de", "--date_end", help="Where to store the data", choices=["kafka", "hbase"])

    ap.add_argument("-dt", "--data_type", required=True, help="Where to store the data",
                    choices=["devices", "supplies", "reading", "all"])

    args = ap.parse_args(arguments)

    # Handle missing parameters
    if (args.data_type != 'reading' or args.data_type != 'all') and args.date_init and args.date_end:
        ap.error('--date_init and --date_end format can only be set when --data_type= [ reading | all ] .')

    if args.data_type == "devices" or args.data_type == "all":
        locations = gather_locations(args, settings, config)
        gather_devices(locations, args, settings, config)

    if args.data_type == "supplies" or args.data_type == "all":
        gather_supplies(args, settings, config, SupplyEnum.ELECTRICITY)
        gather_supplies(args, settings, config, SupplyEnum.WATER)
        gather_supplies(args, settings, config, SupplyEnum.GAS)

    if args.data_type == "reading" or args.data_type == "all":
        date_init = parse(args.date_init)
        date_end = parse(args.date_end)

        if date_init < date_end:
            if abs((date_init - date_end).days) <= 365:
                gather_reads(args, settings, config)
            else:
                raise Exception(
                    "The difference between dates must be less than a year.")
        else:
            raise Exception(
                "Date init must be less than date end.")
