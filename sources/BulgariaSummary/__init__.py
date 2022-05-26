from sources import SourcePlugin
from sources.BulgariaSummary.gather import gather
from sources.BulgariaSummary.harmonizer import harmonize_ts, harmonize_static


class Plugin(SourcePlugin):
    source_name = "bulgariaSummary"

    def gather(self, arguments):
        gather(arguments, settings=self.settings, config=self.config)

    def get_mapper(self, message):
        if message["collection_type"] == 'static':
            return harmonize_static
        elif message["collection_type"] == 'ts':
            return harmonize_ts

    def get_kwargs(self, message):
        return {
            "namespace": message['namespace'],
            "user": message['user'],
            "config": self.config,
            "collection_type": message['collection_type']
        }

    def get_store_table(self, message):
        return f"raw_{self.source_name}_static_{message['collection_type']}__{message['user']}"
