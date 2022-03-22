import argparse
import re

import utils
from sources.Nedgia.harmonizer.mapper_ts import harmonize_data


def harmonize_command_line(arguments, config=None, settings=None):
    ap = argparse.ArgumentParser(description='Mapping of Gas data to neo4j.')
    ap.add_argument("--user", "-u", help="The user importing the data", required=True)
    ap.add_argument("--namespace", "-n", help="The subjects namespace uri", required=True)
    ap.add_argument("--timezone", "-tz", help="The local timezone", required=True, default='Europe/Madrid')
    args = ap.parse_args(arguments)

    hbase_conn = config['hbase_store_raw_data']
    hbase_table = f"nedgia_invoices_{args.user}"

    for data in utils.hbase.get_hbase_data_batch(hbase_conn, hbase_table):
        dic_list = []
        print("parsing hbase")
        for id_, x in data:
            item = dict()
            for k, v in x.items():
                k1 = re.sub("^info:", "", k.decode())
                item[k1] = v
            item.update({"id_": id_})
            dic_list.append(item)
        harmonize_data(dic_list, namespace=args.namespace, user=args.user, config=config, tz_local=args.timezone)
