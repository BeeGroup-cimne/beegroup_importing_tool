import importlib
import json
import pkgutil
from .mongo import mongo_logger
import logging
logging.basicConfig(level=logging.INFO)


def load_plugins(settings):
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


def log_string(text, mongo=True):
    if mongo:
        try:
            mongo_logger.log(text)
        except Exception as e:
            logging.info(f"Error with mongo: {e}")
    logging.error(text)
