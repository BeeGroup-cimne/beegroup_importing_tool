from utils.rdf_utils.bigg_definition import Bigg
from utils.rdf_utils.big_classes import LocationInfo, BuildingSpace, Device, UtilityPointOfDelivery
from slugify import slugify
from utils.data_transformations import *


class Mapping(object):

    def __init__(self, source, namespace):
        self.source = source
        LocationInfo.set_namespace(namespace)
        BuildingSpace.set_namespace(namespace)
        UtilityPointOfDelivery.set_namespace(namespace)
        Device.set_namespace(namespace)

    def get_mappings(self, group):
        location_info = {
            "name": "location_info",
            "class": LocationInfo,
            "type": {
                "origin": "row"
            },
            "params": {
                "mapping": {
                    "subject": {
                        "key": "NumEns",
                        "operations": [id_zfill, location_info_subject]
                    },
                    "addressProvince": {
                        "key": 'province',
                        "operations": [decode_hbase, ]
                    },
                    "addressCity": {
                        "key": 'municipality',
                        "operations": [decode_hbase, ]
                    },
                    "addressPostalCode": {
                        "key":  'postalCode',
                        "operations": [decode_hbase, ]
                    },
                    "addressStreetName": {
                        "key": 'address',
                        "operations": [decode_hbase, ]
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
                        "key": "NumEns",
                        "operations": [id_zfill, slugify, building_space_subject, ]
                    }
                }
            },
            "links": {
                "device": {
                    "type": Bigg.isObservedBy,
                    "link": "cups"
                },
                "utility_point": {
                    "type": Bigg.hasUtilityPointOfDelivery,
                    "link": "cups"
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
                    "utilityType": "electricity"
                },
                "mapping": {
                    "subject": {
                        "key": 'cups',
                        "operations": [decode_hbase, delivery_subject]
                    },
                    "pointOfDeliveryIDFromUser": {
                        "key": 'cups',
                        "operations": [decode_hbase, ]
                    },
                }
            },
            "links": {
                "device": {
                    "type": Bigg.hasDevice,
                    "link": "cups"
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
                    "deviceType": "electricityConsumption"
                },
                "mapping": {
                    "subject": {
                        "key": "cups",
                        "operations": [decode_hbase, partial(device_subject, self.source)]
                    },
                    "deviceName":  {
                        "key": 'cups',
                        "operations": [decode_hbase, ]
                    }
                }
            }
        }

        grouped_modules = {
            "linked": [location_info, building_space, utility_point, device],
            "unlinked": [device]
        }
        return grouped_modules[group]
