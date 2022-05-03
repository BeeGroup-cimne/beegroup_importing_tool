from .transform_functions import get_code_ens
from utils.rdf_utils.ontology.namespaces_definition import Bigg, units, bigg_enums
from utils.rdf_utils.ontology.bigg_classes import BuildingConstructionElement, EnergyEfficiencyMeasure
from utils.data_transformations import *

eem_type_taxonomy = partial(taxonomy_mapping, taxonomy_file="sources/Genercat/harmonizer/EEMTypeTaxonomy.xls",
                            default="Other")

class Mapper(object):

    def __init__(self, source, namespace):
        self.source = source
        BuildingConstructionElement.set_namespace(namespace)
        EnergyEfficiencyMeasure.set_namespace(namespace)

    def get_mappings(self, group):
        building_element = {
            "name": "building_element",
            "class": BuildingConstructionElement,
            "type": {
                "origin": "row"
            },
            "params": {
                "mapping": {
                    "subject": {
                        "key": "element_subject",
                        "operations": []
                    }
                }
            },
            "links": {
                "measures": {
                    "type": Bigg.isAffectedByMeasure,
                    "link": "id_"
                }
            }
        }

        measures = {
            "name": "measures",
            "class": EnergyEfficiencyMeasure,
            "type": {
                "origin": "row"
            },
            "params": {
                "raw": {
                    "hasEnergyEfficiencyMeasureInvestmentCurrency": units["Euro"],
                    "energyEfficiencyMeasureCurrencyExchangeRate": "1",
                },
                "mapping": {
                    "subject": {
                        "key": 'measure_subject',
                        "operations": []
                    },
                    "hasEnergyEfficiencyMeasureType": {
                        "key": 'measurement_type',
                        "operations": []
                    },
                    "energyEfficiencyMeasureDescription": {
                        "key": """Descripció""",
                        "operations": []
                    },
                    "shareOfAffectedElement": {
                        "key": """% de la instal·lació millorada / Potencia FV instal·lada [kW] """,
                        "operations": []
                    },
                    "energyEfficiencyMeasureOperationalDate": {
                        "key": "operation_date",
                        "operations": []
                    },
                    "energyEfficiencyMeasureInvestment": {
                        "key": """Inversió \n(€) \n(IVA no inclòs)""",
                        "operations": []
                    }

                }
            }
        }

        grouped_modules = {
            "all": [building_element, measures],
        }
        return grouped_modules[group]
