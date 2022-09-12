from settings import countries
from utils.rdf_utils.ontology.bigg_classes import Device, LocationInfo


class Mapper(object):
    def __init__(self, source, namespace):
        self.source = source
        Device.set_namespace(namespace)
        LocationInfo.set_namespace(namespace)

    def get_mappings(self, group):
        location = {
            "name": "device",
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
                    "addressAltitude": {
                        "key": "addressAltitude",
                        "operations": []
                    }
                }
            }
        }

        devices = {
            "name": "device",
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
                        "key": "Standard Naming Complex",
                        "operations": []
                    },
                    "deviceName": {
                        "key": "BACnet Name",
                        "operations": []
                    },
                    "observesSpace": {
                        "key": "observesSpace",
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
            "all": [devices],
            "Location": [],
            "Devices": [devices],
        }
        return grouped_modules[group]
