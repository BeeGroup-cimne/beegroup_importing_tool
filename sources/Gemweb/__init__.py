from .gather import gather
from .harmonizer.mapper_static import harmonize_data
from .. import SourcePlugin


class Plugin(SourcePlugin):
    source_name = "gemweb"

    def gather(self, arguments):
        gather(arguments, settings=self.settings, config=self.config)

    def get_mapper(self, message):
        print(f"""received {message["collection_type"]}""")
        if message["collection_type"] == "harmonize":
            return harmonize_data
        else:
            return None

    def get_kwargs(self, message):
        return {
                "namespace": message['namespace'],
                "user": message['user'],
                "config": self.config
        }

    def get_store_table(self, message):
        if message['collection_type'] == "harmonize":
            return None
        else:
            return f"{self.source_name}_{message['collection_type']}_{message['user']}"
