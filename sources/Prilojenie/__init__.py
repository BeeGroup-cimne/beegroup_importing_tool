from sources import SourcePlugin
from sources.Prilojenie.gather import gather
from sources.Prilojenie.harmonizer.mapper import harmonize_general_info


class Plugin(SourcePlugin):
    source_name = "prilojenie"

    def gather(self, arguments):
        gather(arguments, settings=self.settings, config=self.config)

    def get_kwargs(self, message):
        return {
            "namespace": message['namespace'],
            "user": message['user'],
            "config": self.config,
        }

    def get_mapper(self, message):
        if message["collection_type"] == 'generalInfo':
            return harmonize_general_info

        elif message["collection_type"] == 'consumptionInfo':
            return harmonize_general_info

        elif message["collection_type"] == 'distributionInfo':
            return harmonize_general_info

        elif message["collection_type"] == 'energySaved':
            return harmonize_general_info

        elif message["collection_type"] == 'totalAnnualSavings':
            return harmonize_general_info

        elif message["collection_type"] == 'measurements':
            return harmonize_general_info


    def get_store_table(self, message):
        return f"raw_{self.source_name}_static_{message['collection_type']}__{message['user']}"
