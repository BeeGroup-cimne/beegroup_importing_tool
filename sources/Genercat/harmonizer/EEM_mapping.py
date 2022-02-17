from .transform_functions import get_code_ens
from utils.rdf_utils.bigg_definition import Bigg
from utils.rdf_utils.big_classes import BuildingConstructionElement, EnergyEfficiencyMeasure
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
                        "key": 'building_CodeEns_GPG',
                        "operations": [decode_hbase, get_code_ens, id_zfill, construction_element_subject]
                    }
                }
            },
            "links": {
                "measures": {
                    "type": Bigg.isAffectedByMeasures,
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
                    "energyEfficiencyMeasureInvestmentCurrency": "€",
                    "energyEfficiencyMeasureCurrencyExchangeRate": "1",
                },
                "mapping": {
                    "subject": {
                        "key": [
                            {
                                "key": 'building_CodeEns_GPG',
                                "operations": [decode_hbase, get_code_ens, id_zfill]},
                            {
                                "key": "id_",
                                "operations": [decode_hbase]
                            },
                        ],
                        "operations": [partial(join_params, joiner="~"), eem_subject]
                    },
                    "energyEfficiencyMeasureType": {
                        "key": [
                            {
                                "key": 'improvement_type_level1',
                                "operations": [decode_hbase]},
                            {
                                "key": 'improvement_type_level2',
                                "operations": [decode_hbase]
                            },
                            {
                                "key": 'improvement_type_level3',
                                "operations": [decode_hbase]
                            },
                            {
                                "key": 'improvement_type_level4',
                                "operations": [decode_hbase]
                            },
                        ],
                        "operations": [partial(join_params, joiner=".")]
                    },
                    "energyEfficiencyMeasureDescription": {
                        "key": 'description',
                        "operations": [decode_hbase]
                    },
                    "shareOfAffectedElement": {
                        "key": 'improvement_percentage',
                        "operations": [decode_hbase]
                    },
                    "energyEfficiencyMeasureOperationalDate": {
                        "key": 'Data de finalitzaci\xc3\xb3 de l obra / millora',
                        "operations": [decode_hbase]
                    },
                    "energyEfficiencyMeasureInvestment": {
                        "key": 'investment_without_tax',
                        "operations": [decode_hbase]
                    }

                }
            }
        }

        grouped_modules = {
            "all": [building_element, measures],
        }
        return grouped_modules[group]
