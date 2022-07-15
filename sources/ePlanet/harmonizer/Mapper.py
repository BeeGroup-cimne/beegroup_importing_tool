from utils.rdf_utils.ontology.bigg_classes import Building, LocationInfo
from utils.rdf_utils.ontology.namespaces_definition import Bigg, countries


class Mapper(object):
    def __init__(self, source, namespace):
        self.source = source
        Building.set_namespace(namespace)
        LocationInfo.set_namespace(namespace)

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
                    "hasLocationInfo": {
                        "key": "hasLocationInfo",
                        "operations": []
                    }
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

        locations = {
            "name": "locations",
            "class": LocationInfo,
            "type": {
                "origin": "row"
            },
            "params": {
                "raw": {
                    "hasAddressCountry": countries["390903/"]
                },
                "mapping": {
                    "subject": {
                        "key": "location_subject",
                        "operations": []
                    },
                    "addressStreetName": {
                        "key": "Street",
                        "operations": []
                    },
                    "addressStreetNumber": {
                        "key": "Street num",
                        "operations": []
                    },
                    "hasAddressCity": {
                        "key": "hasAddressCity",
                        "operations": []
                    },
                    "hasAddressProvince": {
                        "key": "hasAddressProvince",
                        "operations": []
                    }
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
