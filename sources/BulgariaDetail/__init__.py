import utils
from sources import SourcePlugin
from sources.BulgariaDetail.gather import gather

from sources.BulgariaDetail.harmonizer import harmonize_data

from utils.nomenclature import RAW_MODE


class Plugin(SourcePlugin):
    source_name = "BulgariaDetail"

    def gather(self, arguments):
        gather(arguments, settings=self.settings, config=self.config)

    def get_mapper(self, message):
        if message["collection_type"] == 'harmonize_detail':
            return harmonize_data

    def get_kwargs(self, message):
        if message["collection_type"] == 'harmonize_detail':
            return {
                "namespace": message['namespace'],
                "user": message['user'],
                "config": self.config,
                "collection_type": message['collection_type']
            }

    def get_store_table(self, message):
        if message["collection_type"] == 'BuildingInfo':
            return utils.nomenclature.raw_nomenclature(message['source'], RAW_MODE.STATIC,
                                                       data_type=message["collection_type"],
                                                       frequency="", user=message['user'])
