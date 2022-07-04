import argparse

from utils.gmao import GMAO
from utils.hbase import save_to_hbase
from utils.kafka import save_to_kafka
from utils.nomenclature import raw_nomenclature
from utils.utils import log_string


def gather_zones(g, config, settings, args):
    try:
        total_pages = g.find_zones(page_index=0, page_size=1)['totalpages']
    except Exception as ex:
        g.login()
        total_pages = g.find_zones(page_index=0, page_size=1)['totalpages']
        log_string(ex, mongo=False)

    for i in range(total_pages):
        try:
            data = g.find_zones(page_index=i)['items']
        except Exception as ex:
            log_string(ex, mongo=False)
            g.login()
            data = g.find_zones(page_index=i)['items']

        for zone in data:
            if len(zone['zonepath'].split('.')) == 3:
                print(zone)
                try:
                    full_zone = g.get_full_zone(id=zone['id'], services=['Maintenance'])
                except Exception as ex:
                    log_string(ex)
                    g.login()
                    full_zone = g.get_full_zone(id=zone['id'], services=['Maintenance'])

                save_data([full_zone], data_type='fullZone', row_keys=['id'], column_map=[("info", "all")],
                          config=config, settings=settings, args=args)

        save_data(data=data, data_type='zones', row_keys=['id'],
                  column_map=[("info", "all")],
                  config=config, settings=settings, args=args)


def gather_assets(g: GMAO, config, settings, args):
    try:
        total_pages = g.find_assets(page_index=0, page_size=1)['totalpages']
    except Exception as ex:
        g.login()
        total_pages = g.find_assets(page_index=0, page_size=1)['totalpages']
        log_string(ex, mongo=False)

    for i in range(total_pages):

        try:
            data = g.find_assets(page_index=i)['items']
        except Exception as ex:
            g.login()
            data = g.find_assets(page_index=i)['items']
            log_string(ex, mongo=False)

        for asset in data:
            try:
                full_asset = g.get_full_asset(asset['id'])
            except Exception as ex:
                g.login()
                full_asset = g.get_full_asset(asset['id'])
                log_string(ex, mongo=False)

            save_data(data=[full_asset], data_type='fullAsset', row_keys=['id'],
                      column_map=[("info", "all")],
                      config=config, settings=settings, args=args)

        save_data(data=data, data_type='assets', row_keys=['id'],
                  column_map=[("info", "all")],
                  config=config, settings=settings, args=args)


def gather_data(arguments, config, settings):
    g = GMAO(**config['GMAO'])
    gather_zones(g, config, settings, arguments)
    gather_assets(g, config, settings, arguments)


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
    ap.add_argument("--user", "-u", help="The user importing the data", required=True)
    ap.add_argument("--namespace", "-n", help="The subjects namespace uri", required=True)
    args = ap.parse_args(arguments)
    gather_data(args, config, settings)
