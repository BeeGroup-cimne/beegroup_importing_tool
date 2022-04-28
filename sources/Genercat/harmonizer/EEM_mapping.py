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
                        "key": """ Edifici (Espai)  - Codi Ens (GPG)""",
                        "operations": [decode_hbase, get_code_ens, id_zfill, construction_element_subject]
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
                        "key": [
                            {
                                "key": """ Edifici (Espai)  - Codi Ens (GPG)""",
                                "operations": [decode_hbase, get_code_ens, id_zfill]},
                            {
                                "key": """id_""",
                                "operations": [decode_hbase]
                            },
                        ],
                        "operations": [partial(join_params, joiner="-"), eem_subject]
                    },
                    "hasEnergyEfficiencyMeasureType": {
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
                        "operations": [partial(join_params, joiner="."), eem_type_taxonomy, partial(to_object_property,
                                                                                                    namespace=bigg_enums)]
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
                        "operations": [decode_hbase, pd.Timestamp, pd.Timestamp.isoformat]
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
