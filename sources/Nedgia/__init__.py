from sources import SourcePlugin
from sources.Nedgia.gather import gather
from sources.Nedgia.harmonizer import harmonize_command_line, harmonize_data


class Plugin(SourcePlugin):
    source_name = "nedgia"

    def gather(self, arguments):
        gather(arguments, settings=self.settings, config=self.config)

    def harmonizer_command_line(self, arguments):
        harmonize_command_line(arguments, config=self.config, settings=self.settings)

    def get_mapper(self, message):
        return harmonize_data

    def get_kwargs(self, message):
        return {
            "namespace": message['namespace'],
            "user": message['user'],
            "config": self.config,
            "timezone": message['timezone']
        }
