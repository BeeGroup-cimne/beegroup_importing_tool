from .gather import gather
from .harmonizer import harmonize_command_line
from .harmonizer.mapper_static import harmonize_data
from .. import SourcePlugin


class Plugin(SourcePlugin):
    source_name = "GPG"

    def gather(self, arguments):
        gather(arguments, settings=self.settings, config=self.config)

    def harmonizer_command_line(self, arguments):
        harmonize_command_line(arguments, config=self.config, settings=self.settings)

    def get_mapper(self, message):
        if message["collection_type"] == "buildings":
            print(message["collection_type"])
            return harmonize_data
        else:
            return None

    def get_kwargs(self, message):
        return {
            "namespace": message['namespace'],
            "user": message['user'],
            "organizations": True,
            "config": self.config
        }
