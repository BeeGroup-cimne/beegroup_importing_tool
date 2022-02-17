# import os
# import re
# import settings
# import argparse
# from utils import get_hbase_data_batch, read_config
# from Weather.mapper_ts import map_data as map_data_ts
# source = "weather"
#
#
# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(description='Mapping of Weather data to neo4j.')
#     if os.getenv("PYCHARM_HOSTED"):
#         args_t = []
#         args = parser.parse_args(args_t)
#     else:
#         args = parser.parse_args()
#     # read config file
#     config = read_config(settings.conf_file)
#     hbase_conn = config['hbase_weather_data']
#     h_table_name = config['weather_table']
#     freq = "1h"
#     for data in get_hbase_data_batch(hbase_conn, h_table_name, batch_size=100000):
#         data_list = []
#         for key, row in data:
#             item = dict()
#             for k, v in row.items():
#                 k1 = re.sub("^info:", "", k.decode())
#                 k1 = re.sub("^v:", "", k1)
#                 item[k1] = v
#             lat, lon, ts = key.decode().split("~")
#             item.update({"stationid": f"{float(lat):.3f}~{float(lon):.3f}"})
#             item.update({"timestamp": ts.encode("utf-8")})
#             data_list.append(item)
#         if len(data_list) <= 0:
#             continue
#         map_data_ts(data_list, freq=freq, namespace=args.namespace, user=args.user, config=config, source=source)
#
