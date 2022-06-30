from .gather import gather
from .harmonizer import harmonize_command_line
from .harmonizer.mapper_static import harmonize_IdentificacionEdificio as harmonize_building, \
    harmonize_DatosGeneralesyGeometria as harmonize_area,\
    harmonize_CondicionesFuncionamientoyOcupacion as harmonize_spaces
from .. import SourcePlugin


class Plugin(SourcePlugin):
    source_name = "CEEC3X"

    def gather(self, arguments):
        gather(arguments, settings=self.settings, config=self.config)

    def harmonizer_command_line(self, arguments):
        harmonize_command_line(arguments, config=self.config, settings=self.settings)

    def get_mapper(self, message):
        print(message["collection_type"])
        if message["collection_type"] == "IdentificacionEdificio":
            return harmonize_building
        elif message["collection_type"] == "DatosGeneralesyGeometria":
            return harmonize_area
        elif message["collection_type"] == "CondicionesFuncionamientoyOcupacion":
            return harmonize_spaces
        else:
            return None

    def get_kwargs(self, message):
        if message["collection_type"] in ["IdentificacionEdificio", "DatosGeneralesyGeometria",
                                          "CondicionesFuncionamientoyOcupacion"]:
            return {
                "namespace": message['namespace'],
                "user": message['user'],
                "config": self.config
            }
        else:
            return {}

    def get_store_table(self, message):
        if message["collection_type"] in ["IdentificacionEdificio", "DatosGeneralesyGeometria",
                                          "CondicionesFuncionamientoyOcupacion"]:
            return f"raw_{self.source_name}_static_{message['collection_type']}__{message['user']}"
