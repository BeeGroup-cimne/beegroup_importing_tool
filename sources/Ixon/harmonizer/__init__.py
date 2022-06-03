import argparse
import re

import utils
from harmonizer.cache import Cache
from sources.Ixon.harmonizer.mapper_ts import harmonize_data


def harmonize_command_line(arguments, config, settings):
    ap = argparse.ArgumentParser(description='Mapping of Ixon data to neo4j.')
    ap.add_argument("-o", "--organizations", help="Import the organization structure")
    ap.add_argument("--user", "-u", help="The user importing the data", required=True)
    ap.add_argument("--namespace", "-n", help="The subjects namespace uri", required=True)
    args = ap.parse_args(arguments)

    hbase_conn = config['ixon_raw_data']
    hbase_table = f"ixon_data_infraestructures"

    Cache.load_cache()

    for data in utils.hbase.get_hbase_data_batch(hbase_conn, hbase_table, batch_size=1000):
        dic_list = []
        for key, values in data:
            item = dict()
            for key1, value1 in values.items():
                k = re.sub("^info:|^v:", "", key1.decode())
                item.update({k: value1.decode()})
            dic_list.append(item)
            harmonize_data(dic_list, namespace=args.namespace, user=args.user,
                           organizations=args.organizations, config=config)
