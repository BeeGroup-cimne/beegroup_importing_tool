from sources import SourcePlugin
from sources.BulgariaDetail.gather import gather
from sources.BulgariaDetail.harmonizer.mapper import *


class Plugin(SourcePlugin):
    source_name = "bulgariaDetail"

    def gather(self, arguments):
        gather(arguments, settings=self.settings, config=self.config)

    def get_kwargs(self, message):
        return {
            "namespace": message['namespace'],
            "user": message['user'],
            "config": self.config,
            "collection_type": message['collection_type']
        }

    def get_mapper(self, message):
        if message["collection_type"] == 'harmonize':
            return harmonize_data

    def get_store_table(self, message):
        if message['collection_type'] == 'harmonize':
            return None
        else:
            return f"raw_{self.source_name}_static_{message['collection_type']}__{message['user']}"
