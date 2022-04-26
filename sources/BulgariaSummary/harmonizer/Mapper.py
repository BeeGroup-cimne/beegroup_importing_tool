from slugify import slugify

from utils.rdf_utils.big_classes import Organization, Building


class Mapper(object):
    def __init__(self, source, namespace):
        self.source = source
        Organization.set_namespace(namespace)
        # Building.set_namespace(namespace)

    def get_mappings(self, group):
        organization = {
            "name": "organization",
            "class": Organization,
            "type": {
                "origin": "static"
            },
            "params": {
                "raw": {
                    "subject": slugify("bulgaria"),
                    "organizationName": "Bulgaria",
                    "organizationDivisionType": "Department"
                }
            }
        }

        grouped_modules = {
            "all": [organization],
        }

        return grouped_modules[group]
