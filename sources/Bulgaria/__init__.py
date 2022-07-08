import utils
from sources import SourcePlugin
from sources.Bulgaria.gather import gather
from sources.Bulgaria.harmonizer import harmonize_command_line
from sources.Bulgaria.harmonizer.mapper_buildings import harmonize_ts, harmonize_static, harmonize_detail
from utils.nomenclature import RAW_MODE


class Plugin(SourcePlugin):
    source_name = "bulgaria"

    def gather(self, arguments):
        gather(arguments, settings=self.settings, config=self.config)

    def get_mapper(self, message):
        if message["collection_type"] == 'BuildingInfo':
            return harmonize_static
        elif message["collection_type"] == 'ts':
            return harmonize_ts
        elif message['collection_type'] == 'harmonize_detail':
            return harmonize_detail

    def get_kwargs(self, message):
        return {
            "namespace": message['namespace'],
            "user": message['user'],
            "config": self.config,
            "collection_type": message['collection_type']
        }

    def get_store_table(self, message):
        if message['collection_type'] != 'harmonize_detail':
            return f"raw_{self.source_name}_static_{message['collection_type']}__{message['user']}"
        elif message["collection_type"] == 'BuildingInfo':
            return utils.nomenclature.raw_nomenclature("Bulgaria", RAW_MODE.STATIC, data_type="BuildingInfo",
                                                       user={message['user']})
        else:
            return None

    def harmonizer_command_line(self, arguments):
        harmonize_command_line(arguments, config=self.config, settings=self.settings)
