from sources import SourcePlugin
from sources.Czech.gather import gather


class Plugin(SourcePlugin):
    source_name = "Czech"

    def gather(self, arguments):
        gather(arguments, settings=self.settings, config=self.config)

    # def get_mapper(self, message):
    #     if message["collection_type"] == 'static':
    #         return harmonize_devices
    #     elif message["collection_type"] == 'ts':
    #         return harmonize_ts
    #
    # def get_kwargs(self, message):
    #     return {
    #         "namespace": message['namespace'],
    #         "user": message['user'],
    #         "config": self.config
    #     }
    #
    # def get_store_table(self, message):
    #     if message["collection_type"] == "static":
    #         return f"{self.source_name}_{message['collection_type']}_devices__{message['user']}"
    #     elif message["collection_type"] == "ts":
    #         return f"{self.source_name}_{message['collection_type']}_Meter_PT15M_{message['user']}"
    #     else:
    #         return None
