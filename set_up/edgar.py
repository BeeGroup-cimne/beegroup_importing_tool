import os
import re
from datetime import timedelta

import pandas as pd
from rdflib import RDF, Literal

import settings
import argparse
import rdflib
from utils.rdf_utils.bigg_definition import Bigg

from utils.hbase import get_hbase_data_batch
from utils.utils import read_config


def create_device_list(cups, df_grouped, namespace="https://edgar.com#"):
    g = rdflib.graph.Graph()
    subject_d = Literal(f"{namespace}device-{cups}")
    subject_l = Literal(f"{namespace}measures-{cups}")
    g.add((subject_d, RDF.type, Bigg.Device))
    g.add((subject_d, Bigg.deviceName, Literal(cups)))
    g.add((subject_d, Bigg.deviceType, Literal("Meter")))

    g.add((subject_l, RDF.type, Bigg.MeasurementList))
    g.add((subject_l, Bigg.measurementUnit, Literal("kWh")))
    g.add((subject_l, Bigg.measuredProperty, Literal("ElectricityConsumption")))
    g.add((subject_l, Bigg.measurementReadingType, Literal("Real")))

    g.add((subject_d, Bigg.hasMeasurementLists, subject_l))

    for _, x in df_grouped.iterrows():
        r_subj = Literal(f"{namespace}point-{x.cups}-{x.measurement_ini:%Y-%m-%dT%H:%M:%S}")
        g.add((r_subj, RDF.type, Bigg["Measurement"]))
        g.add((r_subj, Bigg["measurementStart"], Literal(x["measurement_ini"])))
        g.add((r_subj, Bigg["measurementEnd"], Literal(x["measurement_ini"] + timedelta(seconds=3600))))
        g.add((r_subj, Bigg["measurementValue"], Literal(x["consumptionKWh"])))
        g.add((subject_l, Bigg['hasMeasurement'], r_subj))
    return g


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Mapping of Weather data to neo4j.')
    if os.getenv("PYCHARM_HOSTED"):
        args_t = []
        args = parser.parse_args(args_t)
    else:
        args = parser.parse_args()
    # read config file
    config = read_config(settings.conf_file)
    hbase_conn = {
        "host": "master2.internal",
        "port": 9090,
        "table_prefix": "raw_data",
        "table_prefix_separator": ":"
    }

    h_table_name = "datadis_hourly_consumption"
    elems_test = 0
    for data in get_hbase_data_batch(hbase_conn, h_table_name, batch_size=100000):
        print(f"Elements print {elems_test}")
        gr = rdflib.graph.Graph()
        data_list = []
        for key, row in data:
            item = dict()
            for k, v in row.items():
                k1 = re.sub("^info:", "", k.decode())
                k1 = re.sub("^v:", "", k1)
                item[k1] = v.decode()
            device, ts_ini = key.decode().split("~")
            item.update({"cups": device})
            item.update({"measurement_ini": pd.to_datetime(ts_ini, unit="s").to_pydatetime()})
            data_list.append(item)
        if len(data_list) <= 0:
            continue
        df_tmp = pd.DataFrame.from_records(data_list)
        for cups_, df_tmp2 in df_tmp.groupby("cups"):
            gr += create_device_list(cups_, df_tmp2)
        print("Elements_end")
        gr.serialize(destination=f"edgar{elems_test}.tts", format="ttl")
        elems_test += 1
        if elems_test > 10:
            break
