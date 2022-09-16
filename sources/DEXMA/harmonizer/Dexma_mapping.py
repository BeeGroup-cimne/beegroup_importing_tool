from utils.rdf_utils.ontology.bigg_classes import Device, LocationInfo, Building, BuildingSpace, Area
from utils.rdf_utils.ontology.namespaces_definition import bigg_enums, units, countries


class Mapper(object):
    def __init__(self, source, namespace):
        self.source = source
        Device.set_namespace(namespace)
        LocationInfo.set_namespace(namespace)
        Building.set_namespace(namespace)
        BuildingSpace.set_namespace(namespace)
        Area.set_namespace(namespace)
        Device.set_namespace(namespace)

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
                    "addressLatitude": {
                        "key": "address_coordinates_latitude",
                        "operations": []
                    },
                    "addressLongitude": {
                        "key": "address_coordinates_longitude",
                        "operations": []
                    },
                    "addressPostalCode": {
                        "key": "address_country_code",
                        "operations": []
                    },
                    "addressStreetName": {
                        "key": "addressStreetName",
                        "operations": []
                    },
                    "addressStreetNumber": {
                        "key": "addressStreetNumber",
                        "operations": []
                    },
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
                    "buildingIDFromOrganization": {
                        "key": "key",
                        "operations": []
                    },
                    "buildingName": {
                        "key": "name",
                        "operations": []
                    },
                    "hasLocationInfo": {
                        "key": "location_uri",
                        "operations": []
                    },
                    "hasSpace": {
                        "key": "building_space_uri",
                        "operations": []
                    },
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
                    "hasArea": {
                        "key": "hasArea",
                        "operations": []
                    }
                }
            }
        }

        gross_floor_area = {
            "name": "gross_floor_area",
            "class": Area,
            "type": {
                "origin": "row"
            },
            "params": {
                "raw": {
                    "hasAreaType": bigg_enums["GrossFloorAreaAboveGround"],
                    "hasAreaUnitOfMeasurement": units["M2"]
                },
                "mapping": {
                    "subject": {
                        "key": "area_subject",
                        "operations": []
                    },
                    "areaValue": {
                        "key": "area",
                        "operations": []
                    }
                }
            }
        }

        devices = {
            "name": "devices",
            "class": Device,
            "type": {
                "origin": "row"
            },
            "params": {
                "raw": {
                    "deviceNumberOfOutputs": 1,
                },
                "mapping": {
                    "subject": {
                        "key": "device_subject",
                        "operations": []
                    },
                    "deviceIDFromOrganization": {
                        "key": "id_y",
                        "operations": []
                    },
                    "deviceName": {
                        "key": "name_y",
                        "operations": []
                    },
                    "isAssociatedWithSpace": {
                        "key": "building_space_uri",
                        "operations": []
                    },
                    "hasSensor": {
                        "key": "hasSensor",
                        "operations": []
                    },
                    "hasDeviceType": {
                        "key": "hasDeviceType",
                        "operations": []
                    }
                }
            }
        }

        grouped_modules = {
            "Devices-Joined": [location, building, building_space, gross_floor_area, devices],
            "Devices-None": [devices],
        }
        return grouped_modules[group]
