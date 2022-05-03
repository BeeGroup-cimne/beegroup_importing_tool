import hashlib
import settings
from neo4j import GraphDatabase
from rdflib import Namespace
from datetime import timedelta
from utils.hbase import save_to_hbase
from utils.data_transformations import *
from utils.neo4j import get_devices_from_datasource, create_sensor
from utils.rdf_utils.ontology.namespaces_definition import units, bigg_enums

time_to_timedelta = {
    "PT1H": timedelta(hours=1),
    "PT15M": timedelta(minutes=15)
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
    df = df.applymap(decode_hbase)
    df["ts"] = pd.to_datetime(df['timestamp'].apply(int), unit="s")
    df["bucket"] = (df['timestamp'] // 10000000) % settings.buckets
    df['start'] = df['timestamp'].apply(decode_hbase)
    df['end'] = (df.ts + time_to_timedelta[freq]).astype(int) / 10**9
    df['value'] = df['consumptionKWh']
    df['isReal'] = df['obtainMethod'].apply(lambda x: True if x == "Real" else False)
    for device_id, data_group in df.groupby("cups"):
        data_group.set_index("ts", inplace=True)
        data_group.sort_index(inplace=True)
        # find device with ID imported from source

        dt_ini = data_group.iloc[0].name
        dt_end = data_group.iloc[-1].name
        with neo.session() as session:
            device_neo = get_devices_from_datasource(session, user, device_id, "DatadisSource")
            for d_neo in device_neo:
                device_uri = d_neo["d"].get("uri")
                sensor_id = sensor_subject("datadis", device_id, "EnergyConsumptionGridElectricity", "RAW", freq)
                sensor_uri = str(n[sensor_id])
                measurement_id = hashlib.sha256(sensor_uri.encode("utf-8"))
                measurement_id = measurement_id.hexdigest()
                measurement_uri = str(n[measurement_id])

                create_sensor(session, device_uri, sensor_uri, units["KiloW-HR"],
                              bigg_enums.EnergyConsumptionGridElectricity, bigg_enums.TrustedModel,
                              measurement_uri,
                              False, False, freq, "SUM", dt_ini, dt_end)

                data_group['listKey'] = measurement_id
                device_table = f"harmonized_online_EnergyConsumptionGridElectricity_100_SUM_{freq}_{user}"
                save_to_hbase(data_group.to_dict(orient="records"), device_table, hbase_conn2,
                              [("info", ['end', 'isReal']), ("v", ['value'])],
                              row_fields=['bucket', 'listKey', 'start'])
                period_table = f"harmonized_batch_EnergyConsumptionGridElectricity_100_SUM_{freq}_{user}"
                save_to_hbase(data_group.to_dict(orient="records"), period_table, hbase_conn2,
                              [("info", ['end', 'isReal']), ("v", ['value'])],
                              row_fields=['bucket', 'start', 'listKey'])
