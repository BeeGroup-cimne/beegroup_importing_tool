import hashlib
from datetime import timedelta

import pandas as pd
from neo4j import GraphDatabase
from rdflib import Namespace

import settings
from sources.Ixon.harmonizer.mapper import Mapper
from utils.data_transformations import decode_hbase, device_subject, building_space_subject, sensor_subject
from utils.neo4j import get_device_by_uri
from utils.rdf_utils.rdf_functions import generate_rdf
from utils.rdf_utils.save_rdf import save_rdf_with_source

time_to_timedelta = {
    "PT15M": timedelta(minutes=15)
}


def harmonize_devices(data, **kwargs):
    # todo: taxonomies device type
    namespace = kwargs['namespace']
    config = kwargs['config']
    n = Namespace(namespace)
    df = pd.DataFrame(data)

    df['unique_val'] = df['Description'] + '-' + df['BACnet Type'] + '-' + df['Object ID'].astype(str)
    df['device_subject'] = df.apply(lambda x: device_subject(x['unique_val'], config['source']), axis=1)
    df['observesSpace'] = df.apply(lambda x: n[building_space_subject(x['Description'].replace('-', '_'))], axis=1)
    df['hasSensor'] = df.apply(
        lambda x: n[sensor_subject(device_source=config['source'], device_key=x['device_subject'],
                                   measured_property="OtherMeasurement",
                                   sensor_type="RAW", freq="PT15M")], axis=1)

    mapper = Mapper(config['source'], n)
    g = generate_rdf(mapper.get_mappings("all"), df)

    g.serialize('output.ttl', format="ttl")

    save_rdf_with_source(g, config['source'], config['neo4j'])


def harmonize_ts(data, **kwargs):
    # match(n:bigg__Organization) where n.uri starts with "https://infraestructures.cat" return n limit 1
    namespace = kwargs['namespace']
    config = kwargs['config']
    freq = 'PT15M'

    n = Namespace(namespace)

    neo4j_connection = config['neo4j']
    neo = GraphDatabase.driver(**neo4j_connection)

    df = pd.DataFrame(data)
    df = df[df['building_internal_id'].notna()]

    df[['MAC', 'device_name', 'timestamp']] = df['hbase_key'].str.split('~', expand=True)
    df['unique'] = df['building_internal_id'] + '-' + df['type'] + '-' + df['object_id']

    df["ts"] = pd.to_datetime(df['timestamp'].apply(float), unit="s")
    df["bucket"] = (df['timestamp'].apply(float) // settings.ts_buckets) % settings.buckets
    df['start'] = df['timestamp'].apply(decode_hbase)
    df['end'] = (df.ts + time_to_timedelta[freq]).view(int) / 10 ** 9
    df['value'] = df['value']
    df['isReal'] = True

    for device_id, data_group in df.groupby("unique"):
        data_group.set_index("ts", inplace=True)
        data_group.sort_index(inplace=True)

        with neo.session() as session:
            device_neo = get_device_by_uri(session, device_subject(device_id, config['source']) + '.0')

        # SENSOR
        for d_neo in device_neo:
            device_uri = d_neo["n"].get("uri")
            sensor_id = sensor_subject(device_source=config['source'], device_key=device_id,
                                       measured_property="EnergyConsumptionGridElectricity", sensor_type="RAW",
                                       freq=freq)  # TODO: adapt measured_property
            sensor_uri = str(n[sensor_id])
            measurement_id = hashlib.sha256(sensor_uri.encode("utf-8"))
            measurement_id = measurement_id.hexdigest()
            measurement_uri = str(n[measurement_id])
            # with neo.session() as session:
            #     create_sensor(session, device_uri, sensor_uri, units["KiloW-HR"],
            #                   bigg_enums.EnergyConsumptionGridElectricity, bigg_enums.TrustedModel,
            #                   measurement_uri, True,
            #                   False, False, freq, "SUM", dt_ini, dt_end, settings.namespace_mappings)

            # HBASE
