import argparse
import math

from utils.gmao import GMAO


def gather_zones(g):
    page_size = 100
    total_pages = math.ceil(g.find_zones(page_index=0, page_size=1)['totalcount'] / page_size)

    for i in range(total_pages):
        data = g.find_zones(page_index=i)
        print(data)


def gather_data(arguments, config, settings):
    g = GMAO(**config['GMAO'])
    gather_zones(g)


def gather(arguments, config=None, settings=None):
    ap = argparse.ArgumentParser(description='Gathering data from GMAO')
    ap.add_argument("-st", "--store", required=True, help="Where to store the data", choices=["kafka", "hbase"])
    ap.add_argument("--user", "-u", help="The user importing the data", required=True)
    ap.add_argument("--namespace", "-n", help="The subjects namespace uri", required=True)
    args = ap.parse_args(arguments)
    gather_data(args, config, settings)
