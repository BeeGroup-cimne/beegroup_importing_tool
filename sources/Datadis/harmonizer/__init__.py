import argparse
import re

import happybase

import utils
from utils.hbase import get_hbase_data_batch
from .mapper_static import harmonize_data as harmonize_static_data
from .mapper_ts import harmonize_data as harmonize_ts_data


def harmonize_command_line(arguments, config=None, settings=None):
    ap = argparse.ArgumentParser(description='Mapping of Datadis data to neo4j.')
    ap.add_argument("--user", "-u", help="The main organization name", required=True)
    ap.add_argument("--namespace", "-n", help="The subjects namespace uri", required=True)
    ap.add_argument("--type", "-t", help="The type to import [static] or [ts]", required=True)
    args = ap.parse_args(arguments)
    hbase_conn = config['hbase_store_raw_data']
    i = 0
    if args.type == "static":
        supplies_table = f"raw_Datadis_static_supplies__{args.user}"
        for data in get_hbase_data_batch(hbase_conn, supplies_table, batch_size=100):
            supplies = []
            for cups, data1 in data:
                item = dict()
                for k, v in data1.items():
                    k1 = re.sub("^info:", "", k.decode())
                    item[k1] = v
                item.update({"cups": cups})
                supplies.append(item)
            if len(supplies) <= 0:
                continue
            i += len(supplies)
            print(i)
            harmonize_static_data(supplies, namespace=args.namespace,
                                  user=args.user, source="datadis", config=config)
    elif args.type == "ts":
        hbase = happybase.Connection(**hbase_conn)
        ts_tables = [x for x in hbase.tables() if re.match(rf"raw_Datadis_ts_EnergyConsumptionGridElectricity_.*", x.decode())]
        for h_table_name in ts_tables:
            i = 0
            freq = h_table_name.decode().split("_")[4]
            for data in get_hbase_data_batch(hbase_conn, h_table_name, batch_size=1000000):
                data_list = []
                for key, row in data:
                    item = dict()
                    for k, v in row.items():
                        k1 = re.sub("^info:", "", k.decode())
                        k1 = re.sub("^v:", "", k1)
                        item[k1] = v
                    cups, ts = key.decode().split("~")
                    item.update({"cups": cups.encode("utf-8")})
                    item.update({"timestamp": ts.encode("utf-8")})
                    data_list.append(item)
                if len(data_list) <= 0:
                    continue
                i += len(data_list)
                print(f"{freq}: {i}")
                harmonize_ts_data(data_list, freq=freq, namespace=args.namespace, user=args.user, config=config)
    else:
        raise (NotImplementedError("invalid type: [static, ts]"))
