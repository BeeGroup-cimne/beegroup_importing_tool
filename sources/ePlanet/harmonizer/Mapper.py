from utils.data_transformations import to_object_property
from utils.rdf_utils.ontology.bigg_classes import Building, LocationInfo, BuildingSpace, Device, \
    UtilityPointOfDelivery
from utils.rdf_utils.ontology.namespaces_definition import countries, bigg_enums


class Mapper(object):
    def __init__(self, source, namespace):
        self.source = source
        Building.set_namespace(namespace)
        LocationInfo.set_namespace(namespace)
        BuildingSpace.set_namespace(namespace)
        Device.set_namespace(namespace)
        UtilityPointOfDelivery.set_namespace(namespace)

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
                    "buildingName": {
                        "key": "Name of the building or public lighting",
                        "operations": []
                    },
                    "buildingIDFromOrganization": {
                        "key": "Code",
                        "operations": []
                    },
                    "hasLocationInfo": {
                        "key": "hasLocationInfo",
                        "operations": []
                    },
                    "hasSpace": {
                        "key": "hasSpace",
                        "operations": []
                    },
                    # "pertainsToOrganization": {
                    #     "key": "pertainsToOrganization",
                    #     "operations": []
                    # },
                }
            },
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
                    # "hasBuildingSpaceUseType": {
                    #     "key": "hasBuildingSpaceUseType",
                    #     "operations": []
                    # },
                    "isObservedByDevice": {
                        "key": "isObservedByDevice",
                        "operations": []
                    }
                }
            },
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
            }
        }

        device = {
            "name": "device",
            "class": Device,
            "type": {
                "origin": "row"
            },
            "params": {
                "raw": {
                    "hasDeviceType": to_object_property("Meter.EnergyMeter", namespace=bigg_enums)
                },
                "mapping": {
                    "subject": {
                        "key": "device_subject",
                        "operations": []
                    },
                    "deviceName": {
                        "key": 'Meter Code',
                        "operations": []
                    }
                }
            }
        }

        utility_point = {
            "name": "utility_point",
            "class": UtilityPointOfDelivery,
            "type": {
                "origin": "row"
            },
            "params": {
                "raw": {
                    "hasUtilityType": to_object_property("Electricity", namespace=bigg_enums)
                },
                "mapping": {
                    "subject": {
                        "key": 'utility_point_subject',
                        "operations": []
                    },
                    "pointOfDeliveryIDFromOrganization": {
                        "key": 'Meter Code',
                        "operations": []
                    },
                    "hasDevice": {
                        "key": 'isObservedByDevice',
                        "operations": []
                    }
                }
            }
        }

        grouped_modules = {
            "static": [buildings, locations, building_space, device, utility_point]
        }
        return grouped_modules[group]
