from sources import SourcePlugin
from sources.Ixon.harmonizer import harmonize_devices, harmonize_ts


class Plugin(SourcePlugin):
    source_name = "Ixon"

    def get_mapper(self, message):
        if message["collection_type"] == 'devices':
            return harmonize_devices
        elif message["collection_type"] == 'ts':
            return harmonize_ts

    def get_kwargs(self, message):
        return {
            "namespace": message['namespace'],
            "user": message['user'],
            "config": self.config
        }

    def get_store_table(self, message):
        if message["collection_type"] == "ts" or message["collection_type"] == "devices":
            return None
