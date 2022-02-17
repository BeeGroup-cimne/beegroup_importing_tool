import argparse
import os
import settings
import utils
import importlib


def load_source_plugin(source):
    return importlib.import_module(f"sources.{source}")


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", "-so", required=True, help="The source to gather data from")
    if os.getenv("PYCHARM_HOSTED"):
        args_t = ["-so", "GPG", "-f", "test", "-n", "useles", "-u", "eloi", "-st", "kafka"]
        args, unknown = ap.parse_known_args(args_t)
    else:
        args, unknown = ap.parse_known_args()

    source_plugin = load_source_plugin(args.source)
    source = source_plugin.Plugin(settings=settings)
    source.gather(unknown)
