import json
import pkgutil
from utils import utils


class SourcePlugin(object):
    source_name = None

    def __init__(self, settings=None):
        self.settings = settings
        self.config = utils.read_config(settings.conf_file)
        self.config['data_sources'] = {self.source_name: json.loads(pkgutil.get_data(self.__class__.__module__,
                                                                                     "config.json"))}
        self.config['source'] = self.source_name

    def gather(self, arguments):
        raise NotImplemented

    def harmonizer_command_line(self, arguments):
        raise NotImplemented

    def get_mapper(self, message):
        raise NotImplemented

    def get_kwargs(self, message):
        raise NotImplemented

    def get_store_table(self, message):
        return f"{self.source_name}_{message['collection_type']}_{message['user']}"

    def transform_df(self, df):
        return df
