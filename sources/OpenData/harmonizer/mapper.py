from utils.rdf_utils.ontology.bigg_classes import LocationInfo, CadastralInfo, Building, BuildingSpace, Project, \
    EnergyPerformanceCertificate
from utils.rdf_utils.ontology.namespaces_definition import countries


class Mapper(object):
    def __init__(self, source, namespace):
        self.source = source
        LocationInfo.set_namespace(namespace)
        CadastralInfo.set_namespace(namespace)
        Building.set_namespace(namespace)
        BuildingSpace.set_namespace(namespace)

    def get_mappings(self, group):
        location = {
            "name": "location",
            "class": LocationInfo,
            "type": {
                "origin": "row"
            },
            "params": {
                "raw": {
                    "hasAddressCountry": countries["2510769/"]
                },
                "mapping": {
                    "subject": {
                        "key": "location_subject",
                        "operations": []
                    },
                    "addressStreetName": {
                        "key": "adre_a",
                        "operations": []
                    },
                    "addressStreetNumber": {
                        "key": "numero",
                        "operations": []
                    },
                    "addressPostalCode": {
                        "key": "codi_postal",
                        "operations": []
                    },
                }
            }
        }

        cad_ref = {
            "name": "cad_ref",
            "class": CadastralInfo,
            "type": {
                "origin": "row"
            },
            "params": {
                "mapping": {
                    "subject": {
                        "key": "cadastral_subject",
                        "operations": []
                    },
                    "landArea": {
                        "key": "metres_cadastre",
                        "operations": []
                    },
                    "landCadastralReference": {
                        "key": "referencia_cadastral",
                        "operations": []
                    }
                }
            }
        }

        building = {
            "name": "building",
            "class": Building,
            "type": {
                "origin": "row"
            },
            "params": {
                "mapping": {
                    "subject": {
                        "key": "building_subject",
                        "operations": []
                    },
                    "buildingConstructionYear": {
                        "key": "any_construccio",
                        "operations": []
                    },
                    "hasLocationInfo": {
                        "key": "location_uri",
                        "operations": []
                    },
                    "hasSpace": {
                        "key": "building_uri",
                        "operations": []
                    },
                    "hasCadastralInfo": {
                        "key": "cadastral_uri",
                        "operations": []
                    },
                    "hasEPC": {
                        "key": "building_uri",
                        "operations": []
                    }
                }
            }
        }

        building_space = {
            "name": "building_space",
            "class": BuildingSpace,
            "type": {
                "origin": "row"
            },
            "params": {
                "mapping": {
                    "subject": {
                        "key": "building_space_subject",
                        "operations": []
                    },
                    "hasBuildingSpaceUseType": {
                        "key": "hasBuildingSpaceUseType",
                        "operations": []
                    }
                }
            }
        }

        project = {
            "name": "project",
            "class": Project,
            "type": {
                "origin": "row"
            },
            "params": {
                "mapping": {
                    "subject": {
                        "key": "project_subject",
                        "operations": []
                    },
                    "hasBuildingSpaceUseType": {
                        "key": "hasBuildingSpaceUseType",
                        "operations": []
                    }
                }
            }
        }

        epc = {
            "name": "epc",
            "class": EnergyPerformanceCertificate,
            "type": {
                "origin": "row"
            },
            "params": {
                "mapping": {
                    "subject": {
                        "key": "epc_subject",
                        "operations": []
                    }
                }
            }
        }

        grouped_modules = {
            "all": [location, cad_ref, building, building_space, project, epc]
        }
        return grouped_modules[group]
