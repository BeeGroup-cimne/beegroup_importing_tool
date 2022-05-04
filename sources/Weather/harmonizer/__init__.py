import os
import re
import argparse
from .mapper_ts import harmonize_data
from utils.hbase import get_hbase_data_batch


def harmonize_command_line(arguments, config=None, settings=None):
    parser = argparse.ArgumentParser(description='Mapping of Weather data to neo4j.')
    parser.add_argument("--namespace", "-n", help="The subjects namespace uri", required=True)
    args = parser.parse_args(arguments)
    hbase_conn = config['hbase_weather_data']
    i = 0
    weather_table = "darksky_historical"
    freq = "PT1H"
    for data in get_hbase_data_batch(hbase_conn, weather_table, batch_size=100000):
        data_list = []
        for key, row in data:
            item = dict()
            for k, v in row.items():
                k1 = re.sub("^info:", "", k.decode())
                k1 = re.sub("^v:", "", k1)
                item[k1] = v
            lat, lon, ts = key.decode().split("~")
            item.update({"stationid": f"{float(lat):.3f}~{float(lon):.3f}"})
            item.update({"timestamp": ts.encode("utf-8")})
            data_list.append(item)
        if len(data_list) <= 0:
            continue
        i += len(data_list)
        print(f"{freq}: {i}")
        harmonize_data(data_list, freq=freq, namespace=args.namespace, config=config)

