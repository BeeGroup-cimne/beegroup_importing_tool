from sources import SourcePlugin
from sources.Prilojenie.gather import gather


class Plugin(SourcePlugin):
    source_name = "prilojenie"

    def gather(self, arguments):
        gather(arguments, settings=self.settings, config=self.config)
