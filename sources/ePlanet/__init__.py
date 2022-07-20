from sources import SourcePlugin
from sources.ePlanet.gather import gather
from sources.ePlanet.harmonizer.mapping_data import harmonize_data
from utils.nomenclature import raw_nomenclature, RAW_MODE


class Plugin(SourcePlugin):
    source_name = "ePlanet"

    def gather(self, arguments):
        gather(arguments, settings=self.settings, config=self.config)

    def get_mapper(self, message):
        if message["collection_type"] == 'BuildingInfo':
            return harmonize_data

    def get_kwargs(self, message):
        return {
            "namespace": message['namespace'],
            "user": message['user'],
            "config": self.config
        }

    def get_store_table(self, message):
        return raw_nomenclature(source=self.source_name, mode=RAW_MODE.STATIC, data_type=message["collection_type"],
                                frequency="", user=message['user'])
