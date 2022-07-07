from utils.rdf_utils.ontology.bigg_classes import BuildingSpace, MaintenanceAction


class Mapper(object):

    def __init__(self, source, namespace):
        self.source = source
        BuildingSpace.set_namespace(namespace)
        MaintenanceAction.set_namespace(namespace)

    def get_mappings(self, group):
        building_space = {
            "name": "building_space",
            "class": BuildingSpace,
            "type": {
                "origin": "row"
            },
            "params": {
                "mapping": {
                    "subject": {
                        "key": "buildingSpace_subject",
                        "operations": []
                    },
                    "buildingSpaceIDFromOrganization": {
                        "key": "building_space",
                        "operations": []
                    },
                    "buildingSpaceName": {
                        "key": "name",
                        "operations": []
                    },
                    "hasSubSpace": {
                        "key": "hasSubSpace",
                        "operations": []
                    }
                }
            },
            "links": {
            }
        }

        maintenance_action = {
            "name": "maintenance_action",
            "class": MaintenanceAction,
            "type": {
                "origin": "row"
            },
            "params": {
                "mapping": {
                    "subject": {
                        "key": "subject",
                        "operations": []
                    },
                    "maintenanceActionDate": {
                        "key": "orderdate",
                        "operations": []
                    },
                    "maintenanceActionDescription": {
                        "key": "title",
                        "operations": []
                    },
                }
            },
            "links": {
            }
        }

        grouped_modules = {
            "zones": [building_space],
            "work_order": [maintenance_action]
        }
        return grouped_modules[group]
