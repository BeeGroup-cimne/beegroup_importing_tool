import pytz
from .gather import gather
from .harmonizer.mapper_ts import harmonize_data
from .. import SourcePlugin


class Plugin(SourcePlugin):
    source_name = "weather"

    def gather(self, arguments):
        gather(arguments, settings=self.settings, config=self.config)

    def get_mapper(self, message):
        if message["collection_type"] == "darksky":
            return harmonize_data
        else:
            return None

    def get_kwargs(self, message):
        if message["collection_type"] == "darksky":
            return {
                "namespace": message['namespace'],
                "config": self.config,
                "freq": message['freq']
            }
        else:
            return None

    def transform_df(self, df):
        df['ts'] = df.ts.dt.tz_convert(pytz.UTC)
        df['station_id'] = df.apply(lambda el: f"{float(el.latitude):.3f}~{float(el.longitude):.3f}", axis=1)
        return df

    def get_store_table(self, message):
        return None