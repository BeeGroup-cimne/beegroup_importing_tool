from utils.rdf_utils.ontology.bigg_classes import Project


class Mapper(object):
    def __init__(self, source, namespace):
        self.source = source
        Project.set_namespace(namespace)

    def get_mappings(self, group):
        project = {
            "name": "project",
            "class": Project,
            "type": {
                "origin": "row"
            },
            "params": {
                "raw": {
                },
                "mapping": {
                    "subject": {
                        "key": "project_subject",
                        "operations": []
                    },
                    "hasProjectInvestmentCurrency": {
                        "key": "hasProjectInvestmentCurrency",
                        "operations": []
                    }
                }
            }
        }

        grouped_modules = {
            "all": [project]
        }
        return grouped_modules[group]
