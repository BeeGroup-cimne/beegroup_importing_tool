from sources import SourcePlugin
from sources.GMAO.gather import gather
from sources.GMAO.harmonizer.GMAO_mapping import harmonize_full_zone, harmonize_full_work_order
from utils.nomenclature import raw_nomenclature


class Plugin(SourcePlugin):
    source_name = "GMAO"

    def gather(self, arguments):
        gather(arguments, settings=self.settings, config=self.config)

    def get_mapper(self, message):
        if message["collection_type"] == 'fullZone':
            return harmonize_full_zone
        # TODO: Are useful use assets and indicator values endpoints ?¿

        if message["collection_type"] == 'fullWorkOrder':
            return harmonize_full_work_order
        else:
            return None

    def get_kwargs(self, message):
        return {
            "namespace": message['namespace'],
            "user": message['user'],
            "config": self.config
        }

    def get_store_table(self, message):
        return raw_nomenclature(source=self.source_name, mode='static', data_type=message["collection_type"],
                                user=message['user'])
