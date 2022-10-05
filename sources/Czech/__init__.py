from sources import SourcePlugin
from sources.Czech.gather import gather
from sources.Czech.harmonizer.mapper_data import harmonize_building_info, harmonize_building_emm, \
    harmonize_municipality_ts, harmonize_region_ts


class Plugin(SourcePlugin):
    source_name = "Czech"

    def gather(self, arguments):
        gather(arguments, settings=self.settings, config=self.config)

    def get_mapper(self, message):
        if message["collection_type"] == 'BuildingInfo':
            return harmonize_building_info

        if message["collection_type"] == 'EnergyEfficiencyMeasure':
            return harmonize_building_emm

        if message["collection_type"] == 'municipality_ts':
            return harmonize_municipality_ts

        if message["collection_type"] == 'region_ts':
            return harmonize_region_ts

    def get_kwargs(self, message):
        return {
            "namespace": message['namespace'],
            "user": message['user'],
            "config": self.config
        }

    def get_store_table(self, message):
        return message['table_name']
