import hashlib
import pandas as pd
from neo4j import GraphDatabase
from rdflib import Namespace
from datetime import timedelta
from utils.hbase import save_to_hbase
from utils.data_transformations import *
from utils.utils import log_string

time_to_timedelta = {
    "1h": timedelta(hours=1),
    "15m": timedelta(minutes=15)
}

keys_remap = {'apparentTemperature': 'apparentTemperature', 'cloudCover': 'cloudCover', 'dewPoint': 'dewPoint',
              'humidity': 'humidity', 'icon': 'icon', 'ozone': 'ozone', 'precipIntensity': 'precipIntensity',
              'precipProbability': 'precipProbability', 'precipType': 'precipType', 'pressure': 'pressure',
              'summary': 'summary', 'temperature': 'temperature', 'uvIndex': 'uvIndex', 'visibility': 'visibility',
              'windBearing': 'windBearing', 'windGust': 'windGust', 'windSpeed': 'windSpeed',
              'precipAccumulation': 'precipAccumulation'}


def harmonize_data(data, **kwargs):
    freq = kwargs['freq']
    namespace = kwargs['namespace']
    config = kwargs['config']

    hbase_conn2 = config['hbase_harmonized_data']
    neo4j_connection = config['neo4j']

    neo = GraphDatabase.driver(**neo4j_connection)
    n = Namespace(namespace)
    df = pd.DataFrame.from_records(data)
    df["ts"] = pd.to_datetime(df['ts'])
    df['measurement_ini'] = df["ts"].astype(int) / 10**9
    df['measurement_end'] = (df.ts + time_to_timedelta[freq]).astype(int) / 10**9
    df.rename(keys_remap, inplace=True)

    for v in keys_remap.values():
        if v in df.columns:
            df[v] = df[v].apply(decode_hbase)
    # log_string(f"starting harmonization")
    for station_id, data_group in df.groupby("station_id"):
        data_group.set_index("ts", inplace=True)
        data_group.sort_index(inplace=True)
        # find device with ID imported from source
        dt_ini = data_group.iloc[0].name
        dt_end = data_group.iloc[-1].name
        with neo.session() as session:
            ws_neo = session.run(f"""
            MATCH (n:ns0__WeatherStation{{uri:"{n[station_id]}"}})
            RETURN n            
            """)
            # log_string(f"weather stations")

            for ws_n in ws_neo:
                list_id = f"{station_id}-DEVICE-LIST-RAW-{freq}"
                list_uri = str(n[list_id])
                new_d_id = hashlib.sha256(list_uri.encode("utf-8"))
                new_d_id = new_d_id.hexdigest()
                session.run(f"""
                    MATCH (ws:ns0__WeatherStation{{uri:"{ws_n["n"].get("uri")}"}})
                    MERGE (list: ns0__MeasurementList{{
                        uri: "{list_uri}",
                        ns0__measurementKey: "{new_d_id}",
                        ns0__measurementFrequency: "{freq}"
                    }})<-[:ns0__hasMeasurementLists]-(ws)
                    SET
                        list.ns0__measurementListStart = CASE 
                            WHEN list.ns0__measurementListStart < datetime("{dt_ini.tz_convert("UTC").to_pydatetime().isoformat()}") 
                                THEN list.ns0__measurementListStart 
                                ELSE datetime("{dt_ini.tz_convert("UTC").to_pydatetime().isoformat()}") 
                            END,
                        list.ns0__measurementListEnd = CASE 
                            WHEN list.ns0__measurementListEnd > datetime("{dt_end.tz_convert("UTC").to_pydatetime().isoformat()}") 
                                THEN list.ns0__measurementListStart 
                                ELSE datetime("{dt_end.tz_convert("UTC").to_pydatetime().isoformat()}") 
                            END  
                    return list
                """)
                data_group['listKey'] = new_d_id
                station_table = f"meteo_{freq}_device_"
                save_to_hbase(data_group.to_dict(orient="records"), station_table, hbase_conn2,
                              [("info", ['measurement_end']), ("v", list(keys_remap.values()))], row_fields=['listKey', 'measurement_ini'])
                period_table = f"meteo_{freq}_period_"
                save_to_hbase(data_group.to_dict(orient="records"), period_table, hbase_conn2,
                              [("info", ['measurement_end']), ("v", list(keys_remap.values()))], row_fields=['measurement_ini', 'listKey'])
                print(f"harmonized {station_table}_{station_id}: {len(data_group)}")
                print(data_group.iloc[0].ts)
                print(data_group.iloc[-1].ts)
