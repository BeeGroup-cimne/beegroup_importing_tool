import argparse
import re
import pandas as pd
import utils
from harmonizer.cache import Cache
from utils.utils import log_string
from .mapper import harmonize_data_ts


def harmonize_command_line(arguments, config=None, settings=None):
    ap = argparse.ArgumentParser(description='Mapping of Tariff data to neo4j.')
    ap.add_argument("--user", "-u", help="The user importing the data", required=True)
    ap.add_argument("--namespace", "-n", help="The subjects namespace uri", required=True)
    ap.add_argument("--tariff", "-tar", help="The name to identify the tariff", required=True)
    ap.add_argument("--date_ini", "-di", help="The data where the tariff starts", required=True)
    ap.add_argument("--date_end", "-de", help="The data where the tariff ends", required=True)
    ap.add_argument("--data_source", "-ds", help="The id to identify the source", required=True)

    args = ap.parse_args(arguments)

    hbase_conn = config['hbase_store_raw_data']
    i = 0
    hbase_table = f"raw_simpletariff_ts_tariff_PT1H_{args.user}"
    Cache.load_cache()
    for data in utils.hbase.get_hbase_data_batch(hbase_conn, hbase_table, batch_size=100):
        dic_list = []
        for key, data1 in data:
            item = dict()
            unique_tariff, pos = key.decode().split("~")
            for k, v in data1.items():
                k1 = re.sub("^info:", "", k.decode())
                item[k1] = v
            item.update({"unique_tariff": unique_tariff})
            item.update({"pos": pos})
            dic_list.append(item)
        if len(dic_list) <= 0:
            continue
        i += len(dic_list)
        log_string(i, mongo=False)
        create_tariff([{"name": args.tariff}], namespace=args.namespace, user=args.user, data_source=args.data_source,
                      config=config)
        harmonize_data_ts(dic_list, namespace=args.namespace, user=args.user, config=config, tariff_name=args.tariff,
                          date_ini=args.date_ini, date_end=args.date_end)

