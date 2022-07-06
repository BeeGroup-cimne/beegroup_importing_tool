from sources import SourcePlugin
from sources.GMAO.gather import gather
from sources.GMAO.harmonizer.GMAO_mapping import harmonize_zone, harmonize_full_zone, harmonize_full_assets, \
    harmonize_indicator_values, harmonize_work_orders, harmonize_assets, \
    harmonize_full_work_order
from utils.nomenclature import raw_nomenclature


class Plugin(SourcePlugin):
    source_name = "GMAO"

    def gather(self, arguments):
        gather(arguments, settings=self.settings, config=self.config)

    def get_mapper(self, message):
        if message["collection_type"] == 'zones':
            return harmonize_zone

        # if message["collection_type"] == 'fullZone':
        #     return harmonize_full_zone
        #
        # if message["collection_type"] == 'assets':
        #     return harmonize_assets
        #
        # if message["collection_type"] == 'fullAsset':
        #     return harmonize_full_assets
        #
        # if message["collection_type"] == 'indicatorValues':
        #     return harmonize_indicator_values
        #
        # if message["collection_type"] == 'workOrders':
        #     return harmonize_work_orders
        #
        # if message["collection_type"] == 'fullWorkOrder':
        #     return harmonize_full_work_order

    def get_kwargs(self, message):
        return {
            "namespace": message['namespace'],
            "user": message['user'],
            "config": self.config
        }

    def get_store_table(self, message):
        return raw_nomenclature(source=self.source_name, mode='static', data_type=message["collection_type"],
                                user=message['user'])
