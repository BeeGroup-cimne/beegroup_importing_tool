from utils.rdf_utils.ontology.bigg_classes import Building
from utils.rdf_utils.ontology.namespaces_definition import Bigg


class Mapper(object):
    def __init__(self, source, namespace):
        self.source = source
        Building.set_namespace(namespace)

    def get_mappings(self, group):
        buildings = {
            "name": "buildings",
            "class": Building,
            "type": {
                "origin": "row"
            },
            "params": {
                "raw": {
                },
                "mapping": {
                    "subject": {
                        "key": "building_subject",
                        "operations": []
                    },
                    # "buildingName": {
                    #     "key": "",
                    #     "operations": []
                    # },
                    # "hasBuildingConstructionType": {
                    #     "key": "hasBuildingConstructionType",
                    #     "operations": []
                    # }
                }
            },
            "links": {
                "device": {
                    "type": Bigg.isObservedByDevice,
                    "link": "subject"
                }
            }
        }

        grouped_modules = {
            "static": [buildings]
        }
        return grouped_modules[group]
