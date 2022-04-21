from sources import SourcePlugin
from sources.Prilojenie.gather import gather


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

    def get_store_table(self, message):
        return f"raw_{self.source_name}_static_{message['collection_type']}__{message['user']}"
