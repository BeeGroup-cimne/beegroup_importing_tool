import argparse


def gather_data(arguments, config, settings):
    pass


def gather(arguments, config=None, settings=None):
    ap = argparse.ArgumentParser(description='Gathering data from GMAO')
    ap.add_argument("-st", "--store", required=True, help="Where to store the data", choices=["kafka", "hbase"])
    ap.add_argument("--user", "-u", help="The user importing the data", required=True)
    ap.add_argument("--type", "-t", help="Gather data", choices=['static', 'ts'], required=True)
    ap.add_argument("--namespace", "-n", help="The subjects namespace uri", required=True)
    args = ap.parse_args(arguments)
