import argparse
import re
import utils
from .mapper_static import harmonize_data


def harmonize_command_line(arguments, config=None, settings=None):
    ap = argparse.ArgumentParser(description='Mapping of GPG data to neo4j.')
    ap.add_argument("-o", "--organizations", action='store_true', help="Import the organization structure")
    ap.add_argument("--user", "-u", help="The user importing the data", required=True)
    ap.add_argument("--namespace", "-n", help="The subjects namespace uri", required=True)
    args = ap.parse_args(arguments)

    hbase_conn = config['hbase_store_raw_data']
    hbase_table = f"GPG_buildings_{args.user}"
    for data in utils.hbase.get_hbase_data_batch(hbase_conn, hbase_table):
        dic_list = []
        print("parsing hbase")
        for n_ens, x in data:
            item = dict()
            for k, v in x.items():
                k1 = re.sub("^info:", "", k.decode())
                item[k1] = v
            item.update({"Num_Ens_Inventari": n_ens})
            dic_list.append(item)
        print("parsed. Mapping...")
        harmonize_data(dic_list, namespace=args.namespace, user=args.user,
                       organizations=args.organizations, config=config)
