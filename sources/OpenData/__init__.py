from sources import SourcePlugin


class Plugin(SourcePlugin):
    source_name = "Ixon"

    def gather(self, arguments):
        pass
        # gather(arguments, settings=self.settings, config=self.config)

    def get_mapper(self, message):
        pass

    def get_kwargs(self, message):
        return {
            "namespace": message['namespace'],
            "user": message['user'],
            "config": self.config
        }

    def get_store_table(self, message):
        pass
