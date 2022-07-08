from utils.rdf_utils.ontology.bigg_classes import BuildingSpace, MaintenanceAction, Element


class Mapper(object):

    def __init__(self, source, namespace):
        self.source = source
        BuildingSpace.set_namespace(namespace)
        MaintenanceAction.set_namespace(namespace)
        Element.set_namespace(namespace)

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
                    },
                    "hasBuildingSpaceUseType": {
                        "key": "hasBuildingSpaceUseType",
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
                    "label": {
                        "key": "ordernumber",
                        "operations": []
                    },
                    "comment": {
                        "key": "title",
                        "operations": []
                    },
                    "maintenanceActionDate": {
                        "key": "orderdate",
                        "operations": []
                    },
                    "maintenanceActionDescription": {
                        "key": "description",
                        "operations": []
                    }, "maintenanceActionIsPeriodic": {
                        "key": "maintenanceActionIsPeriodic",
                        "operations": []
                    }, "maintenanceActionName": {
                        "key": "worktype",
                        "operations": []
                    }, "isSubjectToMaintenance": {
                        "key": "isSubjectToMaintenance",
                        "operations": []
                    },
                }
            },
            "links": {
            }
        }

        element = {
            "name": "element",
            "class": Element,
            "type": {
                "origin": "row"
            },
            "params": {
                "mapping": {
                    "subject": {
                        "key": "element_subject",
                        "operations": []
                    }, "isAssociatedWithSpace": {
                        "key": "isAssociatedWithSpace",
                        "operations": []
                    }, "maintainsElement": {
                        "key": "maintainsElement",
                        "operations": []
                    }
                }
            },
            "links": {
            }
        }

        grouped_modules = {
            "zones": [building_space],
            "work_order": [maintenance_action, element]
        }
        return grouped_modules[group]
