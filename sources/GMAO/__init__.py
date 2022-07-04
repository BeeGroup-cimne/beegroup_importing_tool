from sources import SourcePlugin
from sources.GMAO.gather import gather
from utils.nomenclature import raw_nomenclature


class Plugin(SourcePlugin):
    source_name = "GMAO"

    def gather(self, arguments):
        gather(arguments, settings=self.settings, config=self.config)

    def get_mapper(self, message):
        if message["collection_type"] == 'zone':
            pass
        elif message["collection_type"] == 'full_zone':
            pass

    def get_kwargs(self, message):
        return {
            "namespace": message['namespace'],
            "user": message['user'],
            "config": self.config
        }

    def get_store_table(self, message):
        return raw_nomenclature(source=self.source_name, mode='static', data_type=message["collection_type"],
                                user=message['user'])
