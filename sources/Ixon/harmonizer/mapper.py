from utils.rdf_utils.ontology.bigg_classes import Device, Sensor


class Mapper(object):
    def __init__(self, source, namespace):
        self.source = source
        Device.set_namespace(namespace)

    def get_mappings(self, group):
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

        sensors = {
            "name": "sensors",
            "class": Sensor,
            "type": {
                "origin": "row"
            },
            "params": {
                "raw": {
                },
                "mapping": {
                    "subject": {
                        "key": "sensor_subject",
                        "operations": []
                    },
                    "hasMeasuredProperty": {

                    }
                }
            }
        }

        grouped_modules = {
            "all": [devices]

        }
        return grouped_modules[group]
