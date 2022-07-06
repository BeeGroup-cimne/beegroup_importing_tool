import argparse

from sources.GMAO.gmao import GMAO
from utils.hbase import save_to_hbase
from utils.kafka import save_to_kafka
from utils.nomenclature import raw_nomenclature
from utils.utils import log_string
import pandas as pd


def gather_zones(g: GMAO, config, settings, args):
    for i in range(g.get_total_pages('find_zones')):

        data = g.find_zones(page_index=i)['items']

        for zone in data:
            if len(zone['zonepath'].split('.')) == 3:
                full_zone = g.get_full_zone(id=zone['id'], services=['Maintenance'])
                save_data([full_zone], data_type='fullZone', row_keys=['id'], column_map=[("info", "all")],
                          config=config, settings=settings, args=args)

        save_data(data=data, data_type='zones', row_keys=['id'],
                  column_map=[("info", "all")],
                  config=config, settings=settings, args=args)


def gather_assets(g: GMAO, config, settings, args):
    for i in range(g.get_total_pages('find_assets')):

        data = g.find_assets(page_index=i)['items']

        for asset in data:
            full_asset = g.get_full_asset(asset['id'])
            save_data(data=[full_asset], data_type='fullAsset', row_keys=['id'],
                      column_map=[("info", "all")],
                      config=config, settings=settings, args=args)

        save_data(data=data, data_type='assets', row_keys=['id'],
                  column_map=[("info", "all")],
                  config=config, settings=settings, args=args)


def gather_indicator_values(g: GMAO, config, settings, args):
    for i in range(g.get_total_pages('find_indicator_values')):
        data = g.find_indicator_values(page_index=i, service=['Maintenance'])['items']
        df = pd.json_normalize(data, sep='_')
        save_data(data=df.to_dict(orient='records'), data_type='indicatorValues',
                  row_keys=['indicator_id', 'managedscope_id', 'zone_id'],
                  column_map=[("info", "all")],
                  config=config, settings=settings, args=args)


def gather_work_orders(g: GMAO, config, settings, args):
    for i in range(g.get_total_pages('find_work_orders')):
        data = g.find_work_orders(page_index=i, service='Maintenance')['items']
        for work_order in data:
            full_work_order = g.get_full_work_order(id=work_order['id'])
            save_data(data=[full_work_order], data_type='fullWorkOrder', row_keys=['id'],
                      column_map=[("info", "all")],
                      config=config, settings=settings, args=args)

        save_data(data=data, data_type='workOrders', row_keys=['id'],
                  column_map=[("info", "all")],
                  config=config, settings=settings, args=args)


def gather_data(arguments, config, settings):
    g = GMAO(**config['GMAO'])

    if arguments.type == 'zones' or arguments.type == 'all':
        gather_zones(g, config, settings, arguments)

    if arguments.type == 'assets' or arguments.type == 'all':
        gather_assets(g, config, settings, arguments)

    if arguments.type == 'indicators' or arguments.type == 'all':
        gather_indicator_values(g, config, settings, arguments)

    if arguments.type == 'work_orders' or arguments.type == 'all':
        gather_work_orders(g, config, settings, arguments)


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
            h_table_name = raw_nomenclature(source=config['data_sources'][config['source']]['hbase_table'],
                                            mode='static',
                                            data_type=data_type, user=args.user)

            save_to_hbase(data, h_table_name, config['hbase_store_raw_data'], column_map, row_fields=row_keys)
        except Exception as e:
            log_string(f"Error saving datadis supplies to HBASE: {e}")
    else:
        log_string(f"store {config['store']} is not supported")


def gather(arguments, config=None, settings=None):
    ap = argparse.ArgumentParser(description='Gathering data from GMAO')
    ap.add_argument("-st", "--store", required=True, help="Where to store the data", choices=["kafka", "hbase"])
    ap.add_argument("-t", "--type", required=True, help="Type of data that you would to gather",
                    choices=["zones", "assets", "indicators", "work_orders", "all"])
    ap.add_argument("--user", "-u", help="The user importing the data", required=True)
    ap.add_argument("--namespace", "-n", help="The subjects namespace uri", required=True)
    args = ap.parse_args(arguments)
    gather_data(args, config, settings)
