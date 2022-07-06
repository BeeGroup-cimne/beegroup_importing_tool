from utils.rdf_utils.ontology.bigg_classes import BuildingSpace


class Mapper(object):

    def __init__(self, source, namespace):
        self.source = source
        BuildingSpace.set_namespace(namespace)

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
                        "key": "building_space_subject",
                        "operations": []
                    },
                    "buildingSpaceIDFromOrganization": {
                        "key": "id",
                        "operations": []
                    },
                    "buildingSpaceName": {
                        "key": "name",
                        "operations": []
                    },
                    "label": {
                        "key": "zonepath",
                        "operations": []
                    }
                }
            },
            "links": {
            }
        }

        grouped_modules = {
            "zones": [building_space],
            "full_zones": [building_space],
            "assets": [building_space],
            "full_assets": [building_space],
            "indicator_values": [building_space],
            "work_orders": [building_space],
            "full_work_order": [building_space],
        }
        return grouped_modules[group]
