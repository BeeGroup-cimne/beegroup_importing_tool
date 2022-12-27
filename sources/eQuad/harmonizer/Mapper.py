from utils.rdf_utils.ontology.bigg_classes import Project, Organization, Building, LocationInfo, BuildingSpace, \
    EnergyEfficiencyMeasure, Element, EnergySaving
from utils.rdf_utils.ontology.namespaces_definition import Bigg


class Mapper(object):
    def __init__(self, source, namespace):
        self.source = source
        Project.set_namespace(namespace)
        Organization.set_namespace(namespace)
        Building.set_namespace(namespace)
        BuildingSpace.set_namespace(namespace)
        LocationInfo.set_namespace(namespace)
        EnergyEfficiencyMeasure.set_namespace(namespace)
        Element.set_namespace(namespace)
        EnergySaving.set_namespace(namespace)

    def get_mappings(self, group):
        organization = {
            "name": "organization",
            "class": Organization,
            "type": {
                "origin": "static"
            },
            "params": {
                "raw": {
                    "subject": "eQuad",
                    "organizationName": "eQuad"
                }
            },
            "links": {
                "building_organization": {
                    "type": Bigg.hasSubOrganization,
                    "link": "__all__"
                }
            }
        }

        building_organization = {
            "name": "building_organization",
            "class": Organization,
            "type": {
                "origin": "row"
            },
            "params": {
                "raw": {
                    "organizationDivisionType": "Building"
                },
                "mapping": {
                    "subject": {
                        "key": "organization_subject",
                        "operations": []
                    },
                    "organizationEmail": {
                        "key": "organizationEmail",
                        "operations": []
                    },
                    "organizationTelephoneNumber": {
                        "key": "organizationTelephoneNumber",
                        "operations": []
                    },
                    "organizationName": {
                        "key": "organizationName",
                        "operations": []
                    },
                    "managesBuilding": {
                        "key": "managesBuilding",
                        "operations": []
                    },
                }
            }
        }

        buildings = {
            "name": "buildings",
            "class": Building,
            "type": {
                "origin": "row"
            },
            "params": {
                "mapping": {
                    "subject": {
                        "key": "building_subject",
                        "operations": []
                    },
                    "hasSpace": {
                        "key": "hasSpace",
                        "operations": []
                    },
                    "hasLocationInfo": {
                        "key": "hasLocationInfo",
                        "operations": []
                    },
                    "hasProject": {
                        "key": "hasProject",
                        "operations": []
                    },
                }
            }
        }

        location_info = {
            "name": "location_info",
            "class": LocationInfo,
            "type": {
                "origin": "row"
            },
            "params": {
                "mapping": {
                    "subject": {
                        "key": "location_subject",
                        "operations": []
                    },
                    "addressPostalCode": {
                        "key": "addressPostalCode",
                        "operations": []
                    },
                    "hasAddressCountry": {
                        "key": "addressCountry",
                        "operations": []
                    }
                }
            }
        }

        building_space = {
            "name": "building_space",
            "class": BuildingSpace,
            "type": {
                "origin": "row"
            },
            "params": {
                "raw": {
                    "buildingSpaceName": "Building",
                },
                "mapping": {
                    "subject": {
                        "key": "building_space_subject",
                        "operations": []
                    },
                    "energyEfficiencyMeasureDescription": {
                        "key": "energyEfficiencyMeasureDescription",
                        "operations": []
                    },
                    "energyEfficiencyMeasureInvestmentCurrency": {
                        "key": "energyEfficiencyMeasureInvestmentCurrency",
                        "operations": []
                    },
                    "energyEfficiencyMeasureOperationalDate": {
                        "key": "energyEfficiencyMeasureOperationalDate",
                        "operations": []
                    },
                    "energyEfficiencyMeasureType": {
                        "key": "energyEfficiencyMeasureType",
                        "operations": []
                    },
                    "energyEfficiencyMeasureCO2Reduction": {
                        "key": "energyEfficiencyMeasureCO2Reduction",
                        "operations": []
                    },
                    "energyEfficiencyMeasureFinancialSavings": {
                        "key": "energyEfficiencyMeasureFinancialSavings",
                        "operations": []
                    },
                    "energyEfficiencyMeasureLifetime": {
                        "key": "energyEfficiencyMeasureLifetime",
                        "operations": []
                    },
                    "energySavingEndDate": {
                        "key": "energySavingEndDate",
                        "operations": []
                    },
                    "energySavingStartDate": {
                        "key": "energySavingStartDate",
                        "operations": []
                    },
                    "isAssociatedWithElement": {
                        "key": "element_uri",
                        "operations": []
                    }
                }
            }
        }

        project = {
            "name": "project",
            "class": Project,
            "type": {
                "origin": "row"
            },
            "params": {
                "mapping": {
                    "subject": {
                        "key": "project_subject",
                        "operations": []
                    },
                    "projectDescription": {
                        "key": "projectDescription",
                        "operations": []
                    },
                    "projectName": {
                        "key": "projectName",
                        "operations": []
                    },
                    "projectDiscountRate": {
                        "key": "projectDiscountRate",
                        "operations": []
                    },
                    "projectInterestRate": {
                        "key": "projectInterestRate",
                        "operations": []
                    },
                    "projectInternalRateOfReturn": {
                        "key": "projectInternalRateOfReturn",
                        "operations": []
                    },
                    "projectNetPresentValue": {
                        "key": "projectNetPresentValue",
                        "operations": []
                    },
                    "projectOperationalDate": {
                        "key": "projectOperationalDate",
                        "operations": []
                    },
                    "projectSimplePaybackTime": {
                        "key": "projectSimplePaybackTime",
                        "operations": []
                    },
                    "projectStartDate": {
                        "key": "projectStartDate",
                        "operations": []
                    },
                    "projectInvestment": {
                        "key": "projectInvestment",
                        "operations": []
                    },
                    "projectReceivedGrantFounding": {
                        "key": "projectReceivedGrantFounding",
                        "operations": []
                    },
                    "projectGrantsShareOfCosts": {
                        "key": "projectGrantsShareOfCosts",
                        "operations": []
                    },
                    "hasProjectInvestmentCurrency": {
                        "key": "hasProjectInvestmentCurrency",
                        "operations": []
                    },
                    # "tariffAveragePrice": {
                    #     "key": "tariffAveragePrice",
                    #     "operations": []
                    # }
                }
            }
        }

        element = {
            "name": "project",
            "class": Element,
            "type": {
                "origin": "row"
            },
            "params": {
                "mapping": {
                    "subject": {
                        "key": "element_subject",
                        "operations": []
                    },
                }
            }
        }

        eem = {
            "name": "project",
            "class": EnergyEfficiencyMeasure,
            "type": {
                "origin": "row"
            },
            "params": {
                "mapping": {
                    "subject": {
                        "key": "eem_subject",
                        "operations": []
                    },
                    "energyEfficiencyMeasureDescription": {
                        "key": "energyEfficiencyMeasureDescription",
                        "operations": []
                    },
                    "hasEnergyEfficiencyMeasureInvestmentCurrency": {
                        "key": "energyEfficiencyMeasureInvestmentCurrency",
                        "operations": []
                    },
                    "energyEfficiencyMeasureOperationalDate": {
                        "key": "energyEfficiencyMeasureOperationalDate",
                        "operations": []
                    },
                    # "energyEfficiencyMeasureType": {
                    #     "key": "energyEfficiencyMeasureType",
                    #     "operations": []
                    # },
                    "energyEfficiencyMeasureCO2Reduction": {
                        "key": "energyEfficiencyMeasureCO2Reduction",
                        "operations": []
                    },
                    "energyEfficiencyMeasureFinancialSavings": {
                        "key": "energyEfficiencyMeasureFinancialSavings",
                        "operations": []
                    },
                    "energyEfficiencyMeasureLifetime": {
                        "key": "energyEfficiencyMeasureLifetime",
                        "operations": []
                    },
                    "affectsElement": {
                        "key": "affectsElement",
                        "operations": []
                    },
                    "producesSaving": {
                        "key": "producesSaving",
                        "operations": []
                    },
                }
            }
        }

        energy_saving = {
            "name": "project",
            "class": EnergySaving,
            "type": {
                "origin": "row"
            },
            "params": {
                "mapping": {
                    "subject": {
                        "key": "energy_saving_subject",
                        "operations": []
                    },
                    "energySavingEndDate": {
                        "key": "energySavingEndDate",
                        "operations": []
                    },
                    "energySavingStartDate": {
                        "key": "energySavingStartDate",
                        "operations": []
                    },
                    # "energySavingType": {
                    #     "key": "energySavingType",
                    #     "operations": []
                    # }
                }
            }
        }

        grouped_modules = {
            "project": [organization, building_organization, buildings, location_info, building_space, project,
                        element],
            "eem": [eem, energy_saving]
        }
        return grouped_modules[group]
