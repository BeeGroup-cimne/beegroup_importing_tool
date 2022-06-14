from utils.data_transformations import to_object_property
from utils.rdf_utils.ontology.bigg_classes import Device
from utils.rdf_utils.ontology.namespaces_definition import bigg_enums


class Mapper(object):
    def __init__(self, source, namespace):
        self.source = source
        Device.set_namespace(namespace)

    def get_mappings(self, group):
        # observesSpace, hasSensor
        devices = {
            "name": "device",
            "class": Device,
            "type": {
                "origin": "row"
            },
            "params": {
                "raw": {
                    "hasDeviceType": to_object_property("Meter", namespace=bigg_enums),
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
                    }
                }
            }
        }

        grouped_modules = {
            "all": [devices]

        }
        return grouped_modules[group]
