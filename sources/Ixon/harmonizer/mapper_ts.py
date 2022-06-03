from datetime import timedelta
import pandas as pd

import settings
from utils.data_transformations import decode_hbase

time_to_timedelta = {
    "PT1H": timedelta(hours=1),
    "PT15M": timedelta(minutes=15)
}


def harmonize_data(data, **kwargs):
    namespace = kwargs['namespace']
    user = kwargs['user']
    config = kwargs['config']
    freq = 'PT15M'

    neo4j_connection = config['neo4j']

    df = pd.DataFrame(data)
    df[['MAC', 'device', 'timestamp']] = df['hbase_key'].str.split('~', expand=True)

    df["ts"] = pd.to_datetime(df['timestamp'].apply(float), unit="s")
    df["bucket"] = (df['timestamp'].apply(float) // settings.ts_buckets) % settings.buckets
    df['start'] = df['timestamp'].apply(decode_hbase)
    df['end'] = (df.ts + time_to_timedelta[freq]).view(int) / 10 ** 9
    df['value'] = df['value']
    df['isReal'] = True
