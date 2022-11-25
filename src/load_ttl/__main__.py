import argparse
import os
from load_ttl import load_ttl_to_neo4j

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Load ttl and JSON to database')
    parser.add_argument("--directory", "-d", help="The directory to load", required=True)
    parser.add_argument("--user", "-u", help="The user to upload the data", required=True)
    if os.getenv("PYCHARM_HOSTED"):
        args_t = ["-d", "/Users/eloigabal/outputs_bigg", "-u", "icaen"]
        args = parser.parse_args(args_t)
    else:
        args = parser.parse_args()

    load_ttl_to_neo4j(args.directory, args.user)
