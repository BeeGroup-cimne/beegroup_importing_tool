import hashlib
from datetime import datetime

import pandas as pd
from neo4j import GraphDatabase
from rdflib import Namespace

from utils.hbase import save_to_hbase


def harmonize_data_ts(data, **kwargs):
    # Variables
    namespace = kwargs['namespace']
    user = kwargs['user']
    config = kwargs['config']
    tz_info = kwargs['timezone']

    # Database connections

    hbase_conn2 = config['hbase_store_harmonized_data']
    neo4j_connection = config['neo4j']
    neo = GraphDatabase.driver(**neo4j_connection)
    n = Namespace(namespace)

    # Init dataframe
    df = pd.DataFrame.from_records(data)
    # df = pd.read_excel('data/Generalitat Extracción_2018.xlsx',skiprows=2)

    # Add timezone

    df['Fecha fin Docu. cálculo'] += pd.Timedelta(hours=23)

    df['Fecha inicio Docu. cálculo'] = df['Fecha inicio Docu. cálculo'].dt.tz_localize(tz_info)
    df['Fecha fin Docu. cálculo'] = df['Fecha fin Docu. cálculo'].dt.tz_localize(tz_info)

    # datatime64 [ns] to unix time
    df['measurementStart'] = df['Fecha inicio Docu. cálculo'].astype('int') / 10 ** 9
    df['measurementStart'] = df['measurementStart'].astype('int')

    df['measurementEnd'] = df['Fecha fin Docu. cálculo'].astype('int') / 10 ** 9
    df['measurementEnd'] = df['measurementEnd'].astype('int')
    df['ts'] = df['measurementStart']

    # Calculate kWh
    df['measurementValue'] = df['Consumo kWh ATR'].fillna(0) + df['Consumo kWh GLP'].fillna(0)

    df = df[['CUPS', 'ts', 'measurementStart', 'measurementEnd', 'measurementValue']]

    for cups, data_group in df.groupby("CUPS"):
        data_group.set_index("ts", inplace=True)
        data_group.sort_index(inplace=True)

        device_id = cups

        dt_ini = data_group['measurementStart'].iloc[0]
        dt_end = data_group['measurementEnd'].iloc[-1]

        with neo.session() as session:
            n = Namespace(namespace)
            uri = n[f"{device_id}-DEVICE-nedgia"]
            query_devices = f"""
            MATCH (n:ns0__Device{{uri:"{uri}"}}) return n
            """
            devices_list = session.run(query_devices)

            for devices in devices_list:
                list_id = f"{device_id}-DEVICE-{config['source']}-LIST-RAW-invoices"
                list_uri = n[list_id]
                new_d_id = hashlib.sha256(list_uri.encode("utf-8"))
                new_d_id = new_d_id.hexdigest()
                try:
                    query_measures = f"""
                        MATCH (device: ns0__Device {{uri:"{devices["n"].get("uri")}"}})
                        MERGE (list: ns0__MeasurementList{{uri: "{list_uri}", ns0__measurementKey: "{new_d_id}",
                        ns0__measurementFrequency: "invoices"}} )<-[:ns0__hasMeasurementLists]-(device)
                        SET
                            list.ns0__measurementUnit= "kWh",
                            list.ns0__measuredProperty= "gasConsumption",
                            list.ns0__measurementListStart = CASE 
                                WHEN list.ns0__measurementListStart < 
                                 datetime("{datetime.fromtimestamp(dt_ini).isoformat()}") 
                                    THEN list.ns0__measurementListStart 
                                    ELSE datetime("{datetime.fromtimestamp(dt_ini).isoformat()}") 
                                END,
                            list.ns0__measurementListEnd = CASE 
                                WHEN list.ns0__measurementListEnd >
                                 datetime("{datetime.fromtimestamp(dt_end).isoformat()}") 
                                    THEN list.ns0__measurementListStart 
                                    ELSE datetime("{datetime.fromtimestamp(dt_end).isoformat()}") 
                                END  
                        return list
                    """

                    session.run(query_measures)

                    data_group['listKey'] = new_d_id
                    device_table = f"gasConsumption_invoices_device_{user}"
                    save_to_hbase(data_group.to_dict(orient="records"), device_table, hbase_conn2,
                                  [("info", ['measurementEnd']), ("v", ['measurementValue'])],
                                  row_fields=['listKey', 'measurementStart'])

                    period_table = f"gasConsumption_invoices_period_{user}"
                    save_to_hbase(data_group.to_dict(orient="records"), period_table, hbase_conn2,
                                  [("info", ['measurementEnd']), ("v", ['measurementValue'])],
                                  row_fields=['measurementStart', 'listKey'])
                except Exception as ex:
                    print(str(ex))


def harmonize_data_device(data, **kwargs):
    namespace = kwargs['namespace']
    user = kwargs['user']
    config = kwargs['config']

    neo = GraphDatabase.driver(**config['neo4j'])
    n = Namespace(namespace)
    with neo.session() as session:
        nedgia_datasource = session.run(f"""
              MATCH (o:ns0__Organization{{ns0__userId:'{user}'}})-[:ns0__hasSource]->(s:NedgiaSource) return id(s)""").single()

        datasource = nedgia_datasource['id(s)']
        for device in data:

            uri = n[f"{device['device']}-DEVICE-nedgia"]
            try:
                query_create_device = f"""
                MERGE (d:ns0__Device{{ns0__deviceName:"{device['device']}",ns0__deviceType:"gas",
                ns0__source:"nedgia",uri:"{uri}"}}) RETURN d"""

                session.run(query_create_device)

                query_has_device = f""" MATCH (n:ns0__UtilityPointOfDelivery{{ns0__pointOfDeliveryIDFromUser:"{device['device']}"}})
                MATCH (d:ns0__Device{{ns0__deviceName:"{device['device']}",ns0__source:"nedgia"}})
                MERGE (n)-[:ns0__hasDevice]-(d) RETURN d"""

                session.run(query_has_device)

                query_datasource = f"""MATCH (s) WHERE id(s) = {datasource}
                MATCH (d:ns0__Device{{ns0__deviceName:"{device['device']}",ns0__source:"nedgia"}})
                MERGE (s)-[:ns0__importedFromSource]->(d)
                RETURN d
                """

                session.run(query_datasource)
            except Exception as ex:
                print(str(ex))
