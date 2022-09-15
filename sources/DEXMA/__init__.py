from sources import SourcePlugin
from sources.DEXMA.gather import gather
from sources.DEXMA.harmonizer.mapper import harmonize_static, harmonize_ts
from utils.nomenclature import raw_nomenclature, RAW_MODE


class Plugin(SourcePlugin):
    source_name = "DEXMA"

    def gather(self, arguments):
        gather(arguments, settings=self.settings, config=self.config)

    def get_mapper(self, message):
        list_to_map = ['TimeSeries', 'Devices-Joined', 'Devices-None', 'Supplies']
        if message["collection_type"] in list_to_map:
            return harmonize_ts if message["collection_type"] == "TimeSeries" else harmonize_static

    def get_kwargs(self, message):
        return {
            "namespace": message['namespace'],
            "user": message['user'],
            "config": self.config,
            "collection_type": message['collection_type']
        }

    def get_store_table(self, message):
        list_to_save = ['Devices', 'Locations', 'Supplies', 'TimeSeries']
        mode = RAW_MODE.TIMESERIES if message['collection_type'] == 'TimeSeries' else RAW_MODE.STATIC

        if message['collection_type'] in list_to_save:
            return raw_nomenclature(source=self.source_name, mode=mode,
                                    data_type=message['collection_type'],
                                    user=message['user'])
