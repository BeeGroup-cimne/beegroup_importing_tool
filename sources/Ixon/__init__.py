from sources import SourcePlugin
from sources.Ixon.harmonizer import harmonize_command_line


class Plugin(SourcePlugin):
    source_name = "Ixon"

    def harmonizer_command_line(self, arguments):
        harmonize_command_line(arguments, config=self.config, settings=self.settings)

    def get_mapper(self, message):
        return None

    def get_kwargs(self, message):
        return {
            "namespace": message['namespace'],
            "user": message['user'],
            "organizations": True,
            "config": self.config
        }

    def get_store_table(self, message):
        if message["collection_type"] == "buildings":
            return f"raw_{self.source_name}_static_buildings__{message['user']}"
