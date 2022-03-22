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
                        "key": """ Edifici (Espai)  - Codi Ens (GPG)""",
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
                                "key": """ Edifici (Espai)  - Codi Ens (GPG)""",
                                "operations": [decode_hbase, get_code_ens, id_zfill]},
                            {
                                "key": """id_""",
                                "operations": [decode_hbase]
                            },
                        ],
                        "operations": [partial(join_params, joiner="~"), eem_subject]
                    },
                    "energyEfficiencyMeasureType": {
                        "key": [
                            {
                                "key": """Instal·lació millorada \n(NIVELL 1)""",
                                "operations": [decode_hbase]},
                            {
                                "key": """Tipus de millora \n(NIVELL 2)""",
                                "operations": [decode_hbase]
                            },
                            {
                                "key": """Tipus de millora \n(NIVELL 3)""",
                                "operations": [decode_hbase]
                            },
                            {
                                "key": """Tipus de millora \n(NIVELL 4)""",
                                "operations": [decode_hbase]
                            },
                        ],
                        "operations": [partial(join_params, joiner=".")]
                    },
                    "energyEfficiencyMeasureDescription": {
                        "key": """Descripció""",
                        "operations": [decode_hbase]
                    },
                    "shareOfAffectedElement": {
                        "key": """% de la instal·lació millorada / Potencia FV instal·lada [kW] """,
                        "operations": [decode_hbase]
                    },
                    "energyEfficiencyMeasureOperationalDate": {
                        "key": """Data de finalització de l'obra / millora""",
                        "operations": [decode_hbase]
                    },
                    "energyEfficiencyMeasureStartDate": {
                        "key": """Data d'inici\nde l'obra / millora""",
                        "operations": [decode_hbase]
                    },
                    "energyEfficiencyMeasureInvestment": {
                        "key": """Inversió \n(€) \n(IVA no inclòs)""",
                        "operations": [decode_hbase]
                    }

                }
            }
        }

        grouped_modules = {
            "all": [building_element, measures],
        }
        return grouped_modules[group]
