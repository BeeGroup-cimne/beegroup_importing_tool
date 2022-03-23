import pandas as pd
from neo4j import GraphDatabase
from rdflib import Namespace


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

        dt_ini = data_group.iloc[0].name
        dt_end = data_group.iloc[-1].name

        # with neo.session() as session:
        #     device_neo = session.run(f"""
        #     MATCH (ns0__Organization{{ns0__userId:'{user}'}})-[:ns0__hasSubOrganization*0..]->(o:ns0__Organization)-
        #     [:ns0__hasSource]->(s:DatadisSource)<-[:ns0__importedFromSource]-(d)
        #     WHERE d.uri =~ ".*#{device_id}-DEVICE-{config['source']}" return d
        #     """)

        # for d_neo in device_neo:
        #     list_id = f"{device_id}-DEVICE-{config['source']}-LIST-RAW-{freq}"
        #     list_uri = str(n[list_id])
        #     new_d_id = hashlib.sha256(list_uri.encode("utf-8"))
        #     new_d_id = new_d_id.hexdigest()

        # for d_neo in device_neo:
        #     print(d_neo)


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
            uri = f"{namespace}{device['device']}-DEVICE-nedgia"
            query_create_device = f"""MERGE (d:ns0__Device{{ns0__deviceName:"{device['device']}",ns0__deviceType:"gas
            ",ns0__source:nedgia,uri:{uri}}}) RETURN d """

            session.run(query_create_device)

            query_has_device = f""" MATCH (n:ns0__UtilityPointOfDelivery{{ns0__pointOfDeliveryIDFromUser:"{device['device']}"}}) 
            MATCH (d:ns0__Device{{ns0__deviceName:"{device['device']},ns0__source:nedgia"}})
            MERGE (n)-[:ns0__hasDevice]-(d) RETURN d"""

            session.run(query_has_device)

            query_datasource = f"""MATCH (s) WHERE id(s) == {datasource} 
            MATCH (d:ns0__Device{{ns0__deviceName:"{device['device']}"}})
            MERGE (s)-[:ns0__importedFromSource]->(d)
            RETURN d
            """

            session.run(query_datasource)
