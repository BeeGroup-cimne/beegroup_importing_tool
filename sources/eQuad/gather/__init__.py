import argparse
from json import dumps

import pandas as pd
import requests

BASE_URL = "https://staging-c3po.equadcapital.com"
BASE_HEADERS = {'Content-Type': 'application/json;charset=utf-8'}


def get_token(**kwargs):
    response = requests.post(f"{BASE_URL}/authenticate", headers=BASE_HEADERS,
                             data=dumps({"email": kwargs['username'], "password": kwargs['password']}))
    if response.ok:
        return response.json()['token']
    else:
        raise Exception(f"Authentication process receives a {response.status_code}")


def gather_projects(token):
    response = requests.get(f"{BASE_URL}/api/projects?token={token}")

    if response.ok:
        data = response.json()
        df = pd.json_normalize(data, sep='_')
    else:
        raise Exception(f"Gather project receives a {response.status_code}")


def gather(arguments, config=None, settings=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", "-u", help="The user importing the data", required=True)
    ap.add_argument("--namespace", "-n", help="The subjects namespace uri", required=True)
    ap.add_argument("-st", "--store", required=True, help="Where to store the data", choices=["kafka", "hbase"])
    args = ap.parse_args(arguments)

    token = get_token(**config['eQuad'])
    gather_projects(token=token)
