import argparse
import glob
import json
import os

import pandas as pd
import rdflib
from neo4j import GraphDatabase

import settings
from utils.hbase import save_to_hbase
from utils.rdf_utils.save_rdf import __neo4j_import__
from utils.utils import read_config

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Load ttl and JSON to database')
    parser.add_argument("--directory", "-d", help="The directory to load", required=True)
    parser.add_argument("--user", "-u", help="The user to upload the data", required=True)

    config = read_config(settings.conf_file)
    # get namespaces
    if os.getenv("PYCHARM_HOSTED"):
        args_t = ["-d", "/Users/eloigabal/outputs_bigg", "-u", "icaen"]
        args = parser.parse_args(args_t)
    else:
        args = parser.parse_args()

    print(args)
    g_total = rdflib.Graph()
    for x in glob.glob(f"{args.directory}/*.ttl"):
        # load ttl to neo4j
        g = rdflib.Graph()
        g.parse(x)
        neo = GraphDatabase.driver(**config['neo4j'])
        r = g.query(
            """ SELECT ?hash ?kpi ?freq ?R ?C ?O ?agg
                WHERE{ ?s a bigg:SingleKPIAssessment . 
                       ?s bigg:hasSingleKPIPoint ?hash . 
                       ?s bigg:quantifiesKPI ?kpi .
                       ?s bigg:timeSeriesFrequency ?freq .
                       ?s bigg:timeSeriesIsRegular ?R .
                       ?s bigg:timeSeriesIsCumulative ?C .
                       ?s bigg:timeSeriesIsOnChange ?O .
                       ?s bigg:timeSeriesTimeAggregationFunction ?agg .
                    }
        """)
        for hash, kpi, freq, R, C, O, agg in r:
            h_table_online = f"harmonized_online_{kpi.split('#')[1]}_{1 if R else 0}{1 if C else 0}{1 if O else 0}_{agg}_{freq}_{args.user}"
            h_table_batch = f"harmonized_batch_{kpi.split('#')[1]}_{1 if R else 0}{1 if C else 0}{1 if O else 0}_{agg}_{freq}_{args.user}"
            hash = hash.split('#')[1]
            with neo.session() as session:
                with open(x, 'r') as file_ttl:
                    tty = __neo4j_import__(session, file_ttl.read())
                    print(tty)
            hbase_conn2 = config['hbase_store_harmonized_data']

            for x1 in glob.glob(f"{args.directory}/{hash}.json"):
                with open(x1, 'r') as file_json:
                    data = json.load(file_json)
                    for device_k, data_ts in data.items():
                        ts_list = []
                        print(device_k)
                        for data_point in data_ts:
                            ts = int(pd.to_datetime(data_point['start']).timestamp())
                            bucket = (ts // settings.ts_buckets) % settings.buckets
                            try:
                                item = {}
                                item['isReal'] = data_point['isReal']
                                item['end'] = int(pd.to_datetime(data_point['end']).timestamp())
                                item['value'] = data_point['value']
                                item['bucket'] = bucket
                                item['listKey'] = device_k
                                item['start'] = ts
                                ts_list.append(item)
                            except Exception as e:
                                print(device_k, pd.to_datetime(data_point['start']), x)
                        print(h_table_online)
                        save_to_hbase(ts_list, h_table_online, hbase_conn2,
                                      [("info", ['end', 'isReal']), ("v", ['value'])],
                                      row_fields=['bucket', 'listKey', 'start'])
                        save_to_hbase(ts_list, h_table_batch, hbase_conn2,
                                      [("info", ['end', 'isReal']), ("v", ['value'])],
                                      row_fields=['bucket', 'start', 'listKey'])
