import argparse
import os
import time

import pandas as pd

import argparse
import os
import settings
import importlib

from utils.kafka import read_from_kafka
from utils.mongo import mongo_logger
from utils.utils import read_config, load_plugins, log_string


def load_source_plugin(source):
    return importlib.import_module(f"sources.{source}")


def start_harmonizer():
    config = read_config(settings.conf_file)
    sources_available = load_plugins(settings)
    consumer = read_from_kafka(config['kafka']['topic'], config["kafka"]['group_harmonize'],
                               config['kafka']['connection'])
    try:
        for x in consumer:
            start = time.time()
            message = x.value
            df = pd.DataFrame.from_records(message['data'])
            mapper = None
            kwargs_function = {}
            if 'logger' in message:
                mongo_logger.import_log(message['logger'], "harmonize")
            message_part = ""
            if 'message_part' in message:
                message_part = message['message_part']
            for k, v in sources_available.items():
                if message['source'] == k:
                    mapper = v.get_mapper(message)
                    kwargs_function = v.get_kwargs(message)
                    df = v.transform_df(df)
                    break
            if mapper:
                try:
                    mapper(df.to_dict(orient="records"), **kwargs_function)
                    log_string(f"part {message_part} from {message['source']} harmonized successfully", mongo=False)
                except Exception as e:
                    log_string(f"part {message_part} from {message['source']} harmonized error: {e}")
            duration = time.time() - start
            log_string(duration, mongo=False)
    except Exception as e:
        time.sleep(10)
        print(e)


def harmonize_source(g_args):
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", "-so", required=True, help="The source to gather data from")
    args, unknown = ap.parse_known_args(g_args)
    source_plugin = load_source_plugin(args.source)
    source = source_plugin.Plugin(settings=settings)
    source.harmonizer_command_line(unknown)

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("--custom", "-c", action="store_true", help="activate to harmonize from a custom source")
    # if os.getenv("PYCHARM_HOSTED"):
    #     args_t = ["-c", "-so", "GPG", "-n", "https://useles#", "-u", "icaen", "-o"]
    #     args, unknown = ap.parse_known_args(args_t)
    # else:
    args, unknown = ap.parse_known_args()
    if args.custom:
        harmonize_source(unknown)
    else:
        start_harmonizer()
