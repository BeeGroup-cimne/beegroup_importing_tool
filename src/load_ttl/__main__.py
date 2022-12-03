import argparse
import os
import settings
from load_ttl import load_ttl_to_neo4j
from utils.utils import read_config
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Load ttl and JSON to database')
    parser.add_argument("--directory", "-d", help="The directory to load", required=True)
    parser.add_argument("--user", "-u", help="The user to upload the data", required=True)
    if os.getenv("PYCHARM_HOSTED"):
        args_t = ["-d", "/Users/eloigabal/outputs_bigg", "-u", "icaen"]
        args = parser.parse_args(args_t)
    else:
        args = parser.parse_args()
    config = read_config(settings.conf_file)
    load_ttl_to_neo4j(args.directory, args.user, config)
