import pandas as pd

from sources import SourcePlugin
from .gather import gather
from .harmonizer import harmonize_command_line
from .harmonizer.mapper import harmonize_data_ts, create_tariff


class Plugin(SourcePlugin):
    source_name = "simpletariff"

    def gather(self, arguments):
        gather(arguments, settings=self.settings, config=self.config)

    def harmonizer_command_line(self, arguments):
        harmonize_command_line(arguments, config=self.config, settings=self.settings)

    def get_mapper(self, message):
        if message['collection_type'] == "tariff_ts":
            return harmonize_data_ts
        elif message['collection_type'] == "tariff":
            return create_tariff
        else:
            return None

    def get_kwargs(self, message):
        if message['collection_type'] == "tariff_ts":
            return {
                    "namespace": message['namespace'],
                    "user": message['user'],
                    "date_ini": message['date_ini'],
                    "date_end": message['date_end'],
                    "tariff":  message['tariff'],
                    "config": self.config
                }
        elif message['collection_type'] == "tariff":
            return {
                "namespace": message['namespace'],
                "user": message['user'],
                "data_source": message['data_source'],
                "config": self.config
            }
        else:
            return None

    def get_store_table(self, message):
        if message['collection_type'] == "tariff_ts":
            return f"raw_simpletariff_ts_tariff_PT1H_{message['user']}"
        else:
            return None

    def transform_df(self, df):
        if "values" in df.columns:
            return pd.DataFrame.from_records(df.loc[0, "values"])
        else:
            return df
