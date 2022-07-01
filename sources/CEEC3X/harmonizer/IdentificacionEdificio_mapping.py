from utils.data_transformations import *
from utils.rdf_utils.ontology.namespaces_definition import Bigg, bigg_enums, units, countries
from utils.rdf_utils.ontology.bigg_classes import Organization, Building, LocationInfo, CadastralInfo, BuildingSpace, \
    Area, BuildingConstructionElement



class Mapper(object):
    def __init__(self, source, namespace):
        self.source = source
        Organization.set_namespace(namespace)
        Building.set_namespace(namespace)
        LocationInfo.set_namespace(namespace)
        BuildingSpace.set_namespace(namespace)
        CadastralInfo.set_namespace(namespace)
        Area.set_namespace(namespace)
        BuildingConstructionElement.set_namespace(namespace)

    def get_mappings(self, group):
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
                    "buildingIDFromOrganization": {
                        "key": "building_organization_code",
                        "operations": []
                    },
                    "buildingName": {
                        "key": "NombreDelEdificio",
                        "operations": []
                    }
                }
            },
            "links": {
                "location_info": {
                    "type": Bigg.hasLocationInfo,
                    "link": "building_subject"
                },
                "cadastral_info": {
                    "type": Bigg.hasCadastralInfo,
                    "link": "building_subject"
                }
            }
        }

        location_info = {
            "name": "location_info",
            "class": LocationInfo,
            "type": {
                "origin": "row"
            },
            "params": {
                "mapping": {
                    "subject": {
                        "key": "location_subject",
                        "operations": []
                    },
                    "hasAddressProvince": {
                        "key": "hasAddressProvince",
                        "operations": []
                    },
                    "hasAddressCity": {
                        "key": "hasAddressCity",
                        "operations": []
                    },
                    "addressPostalCode": {
                        "key": "CodigoPostal",
                        "operations": []
                    },
                    "addressStreetName": {
                        "key": 'Direccion',
                        "operations": []
                    }
                }
            }
        }

        cadastral_info = {
            "name": "cadastral_info",
            "class": CadastralInfo,
            "type": {
                "origin": "row",
            },
            "params": {
                "mapping": {
                    "subject": {
                        "key": "cadastral_subject",
                        "operations": []
                    },
                    "landCadastralReference": {
                        "key": "ReferenciaCatastral",
                        "operations": []
                    }
                }
            }
        }

        grouped_modules = {
            "all": [building, location_info, cadastral_info]
        }
        return grouped_modules[group]
