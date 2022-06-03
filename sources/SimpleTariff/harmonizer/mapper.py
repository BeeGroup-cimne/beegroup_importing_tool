import hashlib
from datetime import datetime

import pandas as pd
from neo4j import GraphDatabase
from rdflib import Namespace

import settings
from utils.data_transformations import decode_hbase, sensor_subject, device_subject
from utils.hbase import save_to_hbase
from utils.neo4j import get_device_from_datasource, create_sensor
from utils.rdf_utils.ontology.namespaces_definition import units, bigg_enums
from slugify import slugify

def create_tariff(data, **kwargs):
    namespace = kwargs['namespace']
    user = kwargs['user']
    config = kwargs['config']
    data_source = kwargs['data_source']
    tariff_name = pd.DataFrame.from_records(data).loc[0, 'name']
    tariff_name_uri = slugify(tariff_name)
    bigg = settings.namespace_mappings['bigg']
    n = Namespace(namespace)
    device_uri = device_subject(f"{user}-{tariff_name_uri}", "SimpleTariffSource")
    neo4j_connection = config['neo4j']
    neo = GraphDatabase.driver(**neo4j_connection)
    with neo.session() as session:
        session.run(f"""
                    MATCH ({bigg}__Organization{{userID:'{user}'}})-[:{bigg}__hasSubOrganization*0..]->(o:{bigg}__Organization)-
                    [:hasSource]->(s) where id(s) = {data_source}
                    MERGE (s)<-[:importedFromSource]-(d:{bigg}__Tariff:{bigg}__Device:Resource{{uri:"{n[device_uri]}"}})
                    SET d.source="SimpleTariffSource",
                        d.{bigg}__deviceName = ["{tariff_name}"] return d
                    """)

def harmonize_data_ts(data, **kwargs):
    # Variables
    namespace = kwargs['namespace']
    user = kwargs['user']
    config = kwargs['config']
    tariff_name = kwargs['tariff']
    tariff_name_uri = slugify(tariff_name)

    date_ini = kwargs['date_ini']
    date_end = kwargs['date_end']
    # Database connections

    hbase_conn2 = config['hbase_store_harmonized_data']
    neo4j_connection = config['neo4j']
    neo = GraphDatabase.driver(**neo4j_connection)

    # Init dataframe
    df = pd.DataFrame.from_records(data)
    df = df.applymap(decode_hbase)
    df.index = pd.date_range(datetime(2020, 1, 1, 0), datetime(2020, 12, 31, 23), freq="H", tz="UTC")
    df['map'] = df.index.strftime("%m-%d-%H")
    ranged = pd.date_range(date_ini, date_end, freq="H", tz="UTC")

    tariff_df = pd.DataFrame(index=ranged)
    tariff_df['map'] = tariff_df.index.strftime("%m-%d-%H")

    tariff_df['value'] = tariff_df.map.map({k['map']: k['value'] for k in df.to_dict(orient="records")})
    tariff_df['start'] = tariff_df.index.astype('int') / 10 ** 9
    tariff_df['start'] = tariff_df['start'].astype('int')
    tariff_df['end'] = tariff_df['start'] + 3600
    tariff_df['isReal'] = False

    tariff_df['bucket'] = (tariff_df['start'] // settings.ts_buckets) % settings.buckets

    tariff_df = tariff_df[['bucket', 'start', 'end', 'value', 'isReal']]

    tariff_df.sort_index(inplace=True)

    dt_ini = tariff_df.iloc[0].name.tz_convert("UTC").tz_convert(None)
    dt_end = tariff_df.iloc[-1].name.tz_convert("UTC").tz_convert(None)

    with neo.session() as session:
        n = Namespace(namespace)
        devices_neo = list(get_device_from_datasource(session, user, tariff_name, "SimpleTariffSource",
                                                          settings.namespace_mappings))
    for device in devices_neo:
        print(device)
        device_uri = device['d'].get("uri")
        sensor_id = sensor_subject("simpletariff", tariff_name_uri, "EnergyPriceGridElectricity", "RAW", "")
        sensor_uri = str(n[sensor_id])
        measurement_id = hashlib.sha256(sensor_uri.encode("utf-8"))
        measurement_id = measurement_id.hexdigest()
        measurement_uri = str(n[measurement_id])
        with neo.session() as session:
            create_sensor(session, device_uri, sensor_uri, units["Euro"],
                          bigg_enums["Price.EnergyPriceGridElectricity"], bigg_enums.TrustedModel,
                          measurement_uri, True,
                          False, False, "PT1H", "SUM", dt_ini, dt_end, settings.namespace_mappings)

        tariff_df['listKey'] = measurement_id
        device_table = f"harmonized_online_EnergyPriceGridElectricity_100_SUM_PT1H_{user}"

        save_to_hbase(tariff_df.to_dict(orient="records"),
                      device_table,
                      hbase_conn2,
                      [("info", ['end', 'isReal']), ("v", ['value'])],
                      row_fields=['bucket', 'listKey', 'start'])
        period_table = f"harmonized_batch_EnergyPriceGridElectricity_100_SUM_PT1H_{user}"
        save_to_hbase(tariff_df.to_dict(orient="records"),
                      period_table, hbase_conn2,
                      [("info", ['end', 'isReal']), ("v", ['value'])],
                      row_fields=['bucket', 'start', 'listKey'])