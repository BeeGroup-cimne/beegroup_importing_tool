import hashlib
from datetime import datetime

import pandas as pd
from neo4j import GraphDatabase
from rdflib import Namespace

from utils.hbase import save_to_hbase


def harmonize_general_info(data, **kwargs):
    namespace = kwargs['namespace']
    user = kwargs['user']
    config = kwargs['config']

    neo = GraphDatabase.driver(**config['neo4j'])
    n = Namespace(namespace)


def harmonize_consumption_info(data, **kwargs):
    pass


def harmonize_distribution_info(data, **kwargs):
    pass


def harmonize_energy_saved(data, **kwargs):
    pass


def harmonize_total_annual_savings(data, **kwargs):
    pass


def harmonize_measurements(data, **kwargs):
    pass
