from sources import SourcePlugin
from sources.GMAO.gather import gather
from utils.nomenclature import raw_nomenclature


class Plugin(SourcePlugin):
    source_name = "GMAO"

    def gather(self, arguments):
        gather(arguments, settings=self.settings, config=self.config)

    def get_mapper(self, message):
        if message["collection_type"] == 'static':
            pass
        elif message["collection_type"] == 'ts':
            pass

    def get_kwargs(self, message):
        return {
            "namespace": message['namespace'],
            "user": message['user'],
            "config": self.config
        }

    def get_store_table(self, message):
        if message["collection_type"] == "static":
            return f"{self.source_name}_{message['collection_type']}_devices__{message['user']}"
        elif message["collection_type"] == "ts":
            return raw_nomenclature(self.source_name, message['collection_type'])
