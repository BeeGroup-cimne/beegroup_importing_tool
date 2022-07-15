from utils.rdf_utils.ontology.bigg_classes import Building, LocationInfo, BuildingSpace, Organization
from utils.rdf_utils.ontology.namespaces_definition import Bigg, countries


class Mapper(object):
    def __init__(self, source, namespace):
        self.source = source
        Building.set_namespace(namespace)
        LocationInfo.set_namespace(namespace)
        BuildingSpace.set_namespace(namespace)
        Organization.set_namespace(namespace)

    def get_mappings(self, group):
        organization = {
            "name": "organization",
            "class": Organization,
            "type": {
                "origin": "static"
            },
            "params": {
                "raw": {
                    "subject": "ePlanet",
                    "organizationName": "ePlanet"
                }
            },
            "links": {
                "building_organization": {
                    "type": Bigg.hasSubOrganization,
                    "link": "__all__"
                }
            }
        }

        building_organization = {
            "name": "building_organization",
            "class": Organization,
            "type": {
                "origin": "row"
            },
            "params": {
                "raw": {
                    "organizationDivisionType": "Building"
                },
                "mapping": {
                    "subject": {
                        "key": "organization_subject",
                        "operations": []
                    },
                    "organizationName": {
                        "key": "Code",
                        "operations": []
                    }
                }
            },
            "links": {
                "buildings": {
                    "type": Bigg.managesBuilding,
                    "link": "subject"
                }
            }
        }

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

        building_space = {
            "name": "building_space",
            "class": BuildingSpace,
            "type": {
                "origin": "row"
            },
            "params": {
                "raw": {
                    "buildingSpaceName": "Building"
                },
                "mapping": {
                    "subject": {
                        "key": "building_space_subject",
                        "operations": []
                    },
                    "hasBuildingSpaceUseType": {
                        "key": "hasBuildingSpaceUseType",
                        "operations": []
                    },
                }
            },
            "links": {
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
            "static": [buildings, locations, building_space]
        }
        return grouped_modules[group]
