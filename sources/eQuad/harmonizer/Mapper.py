from utils.rdf_utils.ontology.bigg_classes import Project, Organization, Building, LocationInfo, BuildingSpace
from utils.rdf_utils.ontology.namespaces_definition import Bigg


class Mapper(object):
    def __init__(self, source, namespace):
        self.source = source
        Project.set_namespace(namespace)

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
                }
            },
            "links": {
                "buildings": {
                    "type": Bigg.managesBuilding,
                    "link": "subject"
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
                }
            },
            "links": {
                "building_space": {
                    "type": Bigg.hasSpace,
                    "link": "subject"
                },
                "location_info": {
                    "type": Bigg.hasLocationInfo,
                    "link": "subject"
                },
                "project": {
                    "type": Bigg.hasProject,
                    "link": "subject"
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
                        "key": "building_subject",
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
                    "projectTitle": {
                        "key": "projectTitle",
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
                    "projectReceivedGrantFunding": {
                        "key": "projectReceivedGrantFunding",
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
                    "tariffAveragePrice": {
                        "key": "tariffAveragePrice",
                        "operations": []
                    }
                }
            }
        }

        grouped_modules = {
            "all": [organization, building_organization, buildings, location_info, building_space, project],
            "emm": []
        }
        return grouped_modules[group]
