from sources import SourcePlugin
from sources.Cadastre.gather import gather
from utils.nomenclature import raw_nomenclature, RAW_MODE


class Plugin(SourcePlugin):
    source_name = "Cadastre"

    def gather(self, arguments):
        gather(arguments, settings=self.settings, config=self.config)

    def get_mapper(self, message):
        if message["collection_type"] == 'INSPIRE':
            pass
            # return harmonize_static

    def get_kwargs(self, message):
        return {
            "namespace": message['namespace'],
            "user": message['user'],
            "config": self.config,
            "collection_type": message['collection_type']
        }

    def get_store_table(self, message):
        return raw_nomenclature(source=message['source'], mode=RAW_MODE.STATIC,
                                data_type=message['collection_type'], user=message['user'])
