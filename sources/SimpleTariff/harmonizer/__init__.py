import argparse
import re
import pandas as pd
import utils
from harmonizer.cache import Cache
from utils.utils import log_string
#from .mapper import harmonize_data_device, harmonize_data_ts


def harmonize_command_line(arguments, config=None, settings=None):
    ap = argparse.ArgumentParser(description='Mapping of Tariff data to neo4j.')
    ap.add_argument("--user", "-u", help="The user importing the data", required=True)
    ap.add_argument("--namespace", "-n", help="The subjects namespace uri", required=True)
    ap.add_argument("--timezone", "-tz", help="The local timezone", required=True, default='Europe/Madrid')

    args = ap.parse_args(arguments)

    hbase_conn = config['hbase_store_raw_data']
    i = 0
    hbase_table = f"raw_Nedgia_ts_invoices__{args.user}"
    Cache.load_cache()
    for data in utils.hbase.get_hbase_data_batch(hbase_conn, hbase_table, batch_size=100):
        dic_list = []
        for key, data1 in data:
            item = dict()
            cups, ts_ini = key.decode().split("~")
            for k, v in data1.items():
                k1 = re.sub("^info:", "", k.decode())
                item[k1] = v
            item.update({"CUPS": cups})
            item.update({"Fecha inicio Docu. cálculo": ts_ini})
            dic_list.append(item)
        if len(dic_list) <= 0:
            continue
        i += len(dic_list)
        log_string(i, mongo=False)
        df = pd.DataFrame.from_records(dic_list)
        data_raw = pd.DataFrame(data={'CUPS': df['CUPS'].unique(), 'devices': df['CUPS'].unique()}).to_dict(
                orient="records")
        harmonize_data_device(data_raw, namespace=args.namespace, user=args.user, config=config)
        harmonize_data_ts(dic_list, namespace=args.namespace, user=args.user, config=config, timezone=args.timezone)

