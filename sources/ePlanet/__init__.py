from sources import SourcePlugin
from sources.ePlanet.gather import gather
from sources.ePlanet.harmonizer.mapping_data import harmonize_data


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
        return f"{self.source_name}_{message['collection_type']}_BuildingInfo__{message['user']}"
