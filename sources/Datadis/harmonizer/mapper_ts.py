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


def harmonize_data(data, **kwargs):
    freq = kwargs['freq']
    namespace = kwargs['namespace']
    user = kwargs['user']
    config = kwargs['config']

    hbase_conn2 = config['hbase_store_harmonized_data']
    neo4j_connection = config['neo4j']

    neo = GraphDatabase.driver(**neo4j_connection)
    n = Namespace(namespace)
    df = pd.DataFrame.from_records(data)
    df["ts"] = pd.to_datetime(df['timestamp'].apply(decode_hbase).apply(int), unit="s")
    df['measurement_ini'] = df['timestamp'].apply(decode_hbase)
    df['measurement_end'] = (df.ts + time_to_timedelta[freq]).astype(int) / 10**9
    df['value'] = df['consumptionKWh'].apply(decode_hbase)
    for cups, data_group in df.groupby("cups"):
        data_group.set_index("ts", inplace=True)
        data_group.sort_index(inplace=True)
        # find device with ID imported from source
        device_id = decode_hbase(cups)

        dt_ini = data_group.iloc[0].name
        dt_end = data_group.iloc[-1].name
        reading_type = data_group.obtainMethod.apply(decode_hbase).unique().tolist()
        with neo.session() as session:
            device_neo = session.run(f"""
            MATCH (ns0__Organization{{ns0__userId:'{user}'}})-[:ns0__hasSubOrganization*0..]->(o:ns0__Organization)-
            [:ns0__hasSource]->(s:DatadisSource)<-[:ns0__importedFromSource]-(d)
            WHERE d.uri =~ ".*#{device_id}-DEVICE-{config['source']}" return d            
            """)
            for d_neo in device_neo:
                list_id = f"{device_id}-DEVICE-{config['source']}-LIST-RAW-{freq}"
                list_uri = str(n[list_id])
                new_d_id = hashlib.sha256(list_uri.encode("utf-8"))
                new_d_id = new_d_id.hexdigest()
                session.run(f"""
                    MATCH (device: ns0__Device {{uri:"{d_neo["d"].get("uri")}"}})
                    MERGE (list: ns0__MeasurementList {{
                        uri: "{list_uri}",
                        ns0__measurementKey: "{new_d_id}",
                        ns0__measurementUnit: "kWh",
                        ns0__measurementFrequency: "{freq}",
                        ns0__measurementReadingType: "{",".join(reading_type)}",
                        ns0__measuredProperty: "electricityConsumption"
                    }})<-[:ns0__hasMeasurementLists]-(device)
                    SET
                        list.ns0__measurementListStart = CASE 
                            WHEN list.ns0__measurementListStart < 
                             datetime("{dt_ini.tz_localize("UTC").to_pydatetime().isoformat()}") 
                                THEN list.ns0__measurementListStart 
                                ELSE datetime("{dt_ini.tz_localize("UTC").to_pydatetime().isoformat()}") 
                            END,
                        list.ns0__measurementListEnd = CASE 
                            WHEN list.ns0__measurementListEnd >
                             datetime("{dt_end.tz_localize("UTC").to_pydatetime().isoformat()}") 
                                THEN list.ns0__measurementListStart 
                                ELSE datetime("{dt_end.tz_localize("UTC").to_pydatetime().isoformat()}") 
                            END  
                    return list
                """)
                data_group['listKey'] = new_d_id
                device_table = f"electricityConsumption_{freq}_device_{user}"
                save_to_hbase(data_group.to_dict(orient="records"), device_table, hbase_conn2,
                              [("info", ['measurement_end']), ("v", ['value'])],
                              row_fields=['listKey', 'measurement_ini'])
                period_table = f"electricityConsumption_{freq}_period_{user}"
                save_to_hbase(data_group.to_dict(orient="records"), period_table, hbase_conn2,
                              [("info", ['measurement_end']), ("v", ['value'])],
                              row_fields=['measurement_ini', 'listKey'])
                # log_string(f"harmonized {device_table}_{device_id}: {len(data_group)}")
                # log_string(data_group.iloc[0].datetime)
                # log_string(data_group.iloc[-1].datetime)
