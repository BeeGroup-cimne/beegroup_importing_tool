from .transform_functions import get_code_ens
from utils.rdf_utils.ontology.namespaces_definition import Bigg, units, bigg_enums
from utils.rdf_utils.ontology.bigg_classes import BuildingConstructionElement, EnergyEfficiencyMeasure
from utils.data_transformations import *


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
                        "key": """DescripciĆ³""",
                        "operations": []
                    },
                    "shareOfAffectedElement": {
                        "key": """% de la instalĀ·laciĆ³ millorada / Potencia FV instalĀ·lada [kW] """,
                        "operations": []
                    },
                    "energyEfficiencyMeasureOperationalDate": {
                        "key": "operation_date",
                        "operations": []
                    },
                    "energyEfficiencyMeasureInvestment": {
                        "key": """InversiĆ³ \n(ā¬) \n(IVA no inclĆ²s)""",
                        "operations": []
                    }

                }
            }
        }

        grouped_modules = {
            "all": [building_element, measures],
        }
        return grouped_modules[group]
