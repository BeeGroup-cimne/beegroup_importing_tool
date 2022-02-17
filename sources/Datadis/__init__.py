import re
from .gather import gather
from .harmonizer.mapper_static import harmonize_data as harmonize_data_static
from .harmonizer.mapper_ts import harmonize_data as harmonize_data_ts
from .. import SourcePlugin


class Plugin(SourcePlugin):
    source_name = "datadis"

    def gather(self, arguments):
        gather(arguments, settings=self.settings, config=self.config)

    def get_mapper(self, message):
        if message["collection_type"] == "supplies":
            return harmonize_data_static
        elif re.match(r"data_.*", message["collection_type"]):
            return harmonize_data_ts
        else:
            return None

    def get_kwargs(self, message):
        if message["collection_type"] == "supplies":
            return {
                "namespace": message['namespace'],
                "user": message['user'],
                "config": self.config,
            }
        elif re.match(r"data_.*", message["collection_type"]):
            freq = message['collection_type'].split("_")[1]
            return {
                "namespace": message['namespace'],
                "user": message['user'],
                "config": self.config,
                "freq": freq
            }
        else:
            return None
