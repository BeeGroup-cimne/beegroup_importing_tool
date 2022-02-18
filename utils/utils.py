import importlib
import json
import pkgutil
import sys
from .mongo import mongo_logger
import settings
import logging
logging.basicConfig(level=logging.INFO)


def load_plugins():
    sources_available = {}
    for finder, name, is_pkg in pkgutil.iter_modules(['sources']):
        source_module = importlib.import_module(f"{finder.path}.{name}")
        source = source_module.Plugin(settings=settings)
        sources_available[source.source_name] = source
    return sources_available


def read_config(conf_file):
    with open(conf_file) as config_f:
        config = json.load(config_f)
        if 'neo4j' in config:
            config['neo4j']['auth'] = tuple(config['neo4j']['auth'])
        return config


def log_string(text):
    mongo_logger.log(text)
    logging.info(text)
