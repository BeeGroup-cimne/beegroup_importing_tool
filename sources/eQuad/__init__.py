from utils.nomenclature import raw_nomenclature, RAW_MODE
from .gather import gather
from .harmonizer.mapper_equad import harmonize_data
from .. import SourcePlugin


class Plugin(SourcePlugin):
    source_name = "eQuad"

    def gather(self, arguments):
        gather(arguments, settings=self.settings, config=self.config)

    def get_mapper(self, message):
        if message["collection_type"] == "Projects":
            return harmonize_data
        else:
            return None

    def get_kwargs(self, message):
        return {
            "namespace": message['namespace'],
            "user": message['user'],
            "config": self.config,
        }

    def get_store_table(self, message):
        if message["collection_type"] == "Projects":
            return raw_nomenclature(mode=RAW_MODE.STATIC, data_type=message["collection_type"], frequency="",
                                    user=message['user'],
                                    source=message['source'])
