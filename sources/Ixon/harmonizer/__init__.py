import hashlib
from datetime import timedelta

import numpy as np
import pandas as pd
from neo4j import GraphDatabase
from rdflib import Namespace

import settings
import utils.utils
from sources.Ixon.harmonizer.mapper import Mapper
from utils.data_transformations import decode_hbase, device_subject, building_space_subject, sensor_subject, \
    to_object_property
from utils.neo4j import get_device_by_uri, create_sensor
from utils.rdf_utils.ontology.namespaces_definition import bigg_enums, units
from utils.rdf_utils.rdf_functions import generate_rdf
from utils.rdf_utils.save_rdf import save_rdf_with_source

time_to_timedelta = {
    "PT15M": timedelta(minutes=15)
}


def harmonize_devices(data, **kwargs):
    namespace = kwargs['namespace']
    config = kwargs['config']
    n = Namespace(namespace)
    df = pd.DataFrame(data)

    taxonomy = utils.utils.read_config('utils/tax/ixon_tax.json')
    df['Object ID'] = df['Object ID'].fillna(0).astype(np.int64)
    df['unique_val'] = df['Description'] + '-' + df['BACnet Type'] + '-' + df['Object ID'].astype(str)
    df['device_subject'] = df.apply(lambda x: device_subject(x['unique_val'], config['source']), axis=1)

    df['observesSpace'] = df.apply(lambda x: n[building_space_subject(x['Description'])], axis=1)

    df['Tag_raw'] = df['Tag']
    df['measuredProperty'] = df['Tag_raw']

    df = utils.utils.set_taxonomy_to_df(df=df, column_name='Tag', taxonomy=taxonomy['deviceType'])
    df = utils.utils.set_taxonomy_to_df(df=df, column_name='measuredProperty', taxonomy=taxonomy['measuredProperty'])

    df['measuredProperty_link'] = df.apply(lambda x: to_object_property(x['measuredProperty'], namespace=bigg_enums),
                                           axis=1)  # TODO: Check measuredProperty Others / Unknown property

    df['hasDeviceType'] = df.apply(lambda x: to_object_property(x['Tag'], namespace=bigg_enums), axis=1)
    df['sensor_subject'] = df.apply(lambda x: sensor_subject(device_source=config['source'],
                                                             device_key=x['device_subject'],
                                                             measured_property=x['measuredProperty'],
                                                             sensor_type="RAW", freq="PT15M"), axis=1)

    df['hasSensor'] = df.apply(lambda x: n[x['sensor_subject']], axis=1)

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

        dt_ini = data_group.iloc[0].name.tz_convert("UTC").tz_convert(None)
        dt_end = data_group.iloc[-1].name.tz_convert("UTC").tz_convert(None)

        with neo.session() as session:
            res = get_device_by_uri(session, device_subject(device_id, config['source']))

        if res:
            device = res['d']
            sensor = res['s']

            measurement_id = hashlib.sha256(sensor.get('uri').encode("utf-8"))
            measurement_id = measurement_id.hexdigest()
            measurement_uri = str(n[measurement_id])

            with neo.session() as session:
                create_sensor(session, device.get('uri'), sensor.get('uri'), units["KiloW-HR"],
                              bigg_enums[sensor.get('bigg__hasMeasuredProperty')], bigg_enums.TrustedModel,
                              measurement_uri, True,
                              False, False, freq, "SUM", dt_ini, dt_end, settings.namespace_mappings)

            # HBASE
