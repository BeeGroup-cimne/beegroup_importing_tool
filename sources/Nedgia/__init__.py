from sources import SourcePlugin
from sources.Nedgia.gather import gather


class Plugin(SourcePlugin):
    source_name = "nedgia"

    def gather(self, arguments):
        gather(arguments, settings=self.settings, config=self.config)

    def get_kwargs(self, message):
        return {
            "namespace": message['namespace'],
            "user": message['user'],
            "config": self.config,
        }
