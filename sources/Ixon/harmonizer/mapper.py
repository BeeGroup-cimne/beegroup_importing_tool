from utils.rdf_utils.ontology.bigg_classes import Device


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
                    # "organizationDivisionType": "Building"
                },
                "mapping": {
                    "subject": {
                        "key": "device_subject",
                        "operations": []
                    },
                    "deviceIDFromOrganization": {
                        "key": "BACnet Name",
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
