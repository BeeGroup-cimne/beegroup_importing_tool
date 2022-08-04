from utils.rdf_utils.ontology.bigg_classes import Building, LocationInfo, BuildingSpace, Area, \
    EnergyPerformanceCertificate, AreaType, AreaUnitOfMeasurement, RenovationProject, BuildingOwnership, Device, \
    Element, EnergyEfficiencyMeasure, EnergySaving
from utils.rdf_utils.ontology.namespaces_definition import countries, bigg_enums, units


class Mapper(object):
    def __init__(self, source, namespace):
        self.source = source
        Building.set_namespace(namespace)
        BuildingOwnership.set_namespace(namespace)
        LocationInfo.set_namespace(namespace)
        BuildingSpace.set_namespace(namespace)
        Area.set_namespace(namespace)
        EnergyPerformanceCertificate.set_namespace(namespace)
        AreaType.set_namespace(namespace)
        AreaUnitOfMeasurement.set_namespace(namespace)
        RenovationProject.set_namespace(namespace)
        Element.set_namespace(namespace)
        Device.set_namespace(namespace)
        EnergyEfficiencyMeasure.set_namespace(namespace)
        EnergySaving.set_namespace(namespace)

    def get_mappings(self, group):
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
                    "buildingName": {
                        "key": "Name",
                        "operations": []
                    },
                    "buildingIDFromOrganization": {
                        "key": "Unique ID",
                        "operations": []
                    },
                    "buildingConstructionYear": {
                        "key": "YearOfConstruction",
                        "operations": []
                    },
                    "buildingOpeningHour": {
                        "key": "Occupancy hours",
                        "operations": []
                    },
                    "hasLocationInfo": {
                        "key": "hasLocationInfo",
                        "operations": []
                    },
                    # "hasBuildingConstructionType": {
                    #     "key": "hasBuildingConstructionType",
                    #     "operations": []
                    # },
                    "hasBuildingOwnership": {
                        "key": "hasBuildingOwnership",
                        "operations": []
                    },
                    "hasEPC": {
                        "key": "hasEPC",
                        "operations": []
                    },
                    "hasProject": {
                        "key": "hasProject",
                        "operations": []
                    },
                    "hasSpace": {
                        "key": "building_space_uri",
                        "operations": []
                    },

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
                    "buildingSpaceName": "Building"
                },
                "mapping": {
                    "subject": {
                        "key": "building_space_subject",
                        "operations": []
                    },
                    "hasBuildingSpaceUseType": {
                        "key": "hasBuildingSpaceUseType",
                        "operations": []
                    },
                    "hasArea": {
                        "key": "hasArea",
                        "operations": []
                    },
                }
            },
        }

        location_info = {
            "name": "location_info",
            "class": LocationInfo,
            "type": {
                "origin": "row"
            },
            "params": {
                "raw": {
                    "hasAddressCountry": countries["3077311/"]
                },
                "mapping": {
                    "subject": {
                        "key": "location_subject",
                        "operations": []
                    },
                    "hasAddressProvince": {
                        "key": "hasAddressProvince",
                        "operations": []
                    },
                    "addressLatitude": {
                        "key": "Latitude",
                        "operations": []
                    },
                    "addressLongitude": {
                        "key": "Longitude",
                        "operations": []
                    },
                    "addressStreetName": {
                        "key": "Road",
                        "operations": []
                    },
                    "addressStreetNumber": {
                        "key": "Road Number",
                        "operations": []
                    },
                    "addressPostalCode": {
                        "key": "PostalCode",
                        "operations": []
                    },
                    # "hasAddressCity": {
                    #     "key": "PostalCode",
                    #     "operations": []
                    # },
                    # "hasAddressProvince": {
                    #     "key": "PostalCode",
                    #     "operations": []
                    # }
                }
            }
        }

        gross_floor_area = {
            "name": "gross_floor_area",
            "class": Area,
            "type": {
                "origin": "row"
            },
            "params": {
                "raw": {
                    "hasAreaType": bigg_enums["GrossFloorAreaAboveGround"],
                    "hasAreaUnitOfMeasurement": units["M2"]
                },
                "mapping": {
                    "subject": {
                        "key": "gross_floor_area_subject",
                        "operations": []
                    },
                    "areaValue": {
                        "key": "GrossFloorArea",
                        "operations": []
                    }
                }
            }
        }

        owner = {
            "name": "owner",
            "class": BuildingOwnership,
            "type": {
                "origin": "row"
            },
            "params": {
                "mapping": {
                    "subject": {
                        "key": "building_ownership_subject",
                        "operations": []
                    }
                }
            },
        }

        energy_performance_certificate = {
            "name": "energy_performance_certificate",
            "class": EnergyPerformanceCertificate,
            "type": {
                "origin": "row"
            },
            "params": {
                "mapping": {
                    "subject": {
                        "key": "energy_performance_certificate_subject",
                        "operations": []
                    },
                    "energyPerformanceCertificateDateOfAssessment": {
                        "key": "EnergyCertificateDate",
                        "operations": []
                    },
                    "energyPerformanceCertificateClass": {
                        "key": "EnergyCertificateQualification",
                        "operations": []
                    }
                }
            }
        }

        project = {
            "name": "project",
            "class": RenovationProject,
            "type": {
                "origin": "row"
            },
            "params": {
                "mapping": {
                    "subject": {
                        "key": "project_subject",
                        "operations": []
                    }
                }
            }
        }

        element = {
            "name": "element",
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
                    "isObservedByDevice": {
                        "key": "device_uri",
                        "operations": []
                    },
                    "isAssociatedWithSpace": {
                        "key": "building_space_uri",
                        "operations": []
                    }
                }
            }
        }

        devices = {
            "name": "devices",
            "class": Device,
            "type": {
                "origin": "row"
            },
            "params": {
                "mapping": {
                    "subject": {
                        "key": "device_subject",
                        "operations": []
                    },
                }
            }
        }

        eem = {
            "name": "eem",
            "class": EnergyEfficiencyMeasure,
            "type": {
                "origin": "row"
            },
            "params": {
                "raw": {
                    "hasEnergyEfficiencyMeasureInvestmentCurrency": units["CzechKoruna"],
                    "energyEfficiencyMeasureCurrencyExchangeRate": "0.041",
                },
                "mapping": {
                    "subject": {
                        "key": "energy_efficiency_measure_subject",
                        "operations": []
                    },
                    "energyEfficiencyMeasureInvestment": {
                        "key": "Investment",
                        "operations": []
                    },
                    "hasEnergyEfficiencyMeasureType": {
                        "key": "hasEnergyEfficiencyMeasureType",
                        "operations": []
                    },
                    "label": {
                        "key": "ETM Name",
                        "operations": []
                    },
                    "energyEfficiencyMeasureCO2Reduction": {
                        "key": "Annual CO2 reduction",
                        "operations": []
                    },
                    "producesSaving": {
                        "key": "producesSaving",
                        "operations": []
                    },
                    "affectsElement": {
                        "key": "element_uri",
                        "operations": []
                    }
                },
            }
        }

        energy_saving = {
            "name": "energy_saving",
            "class": EnergySaving,
            "type": {
                "origin": "row"
            },
            "params": {
                "mapping": {
                    "subject": {
                        "key": "energy_saving_subject",
                        "operations": []
                    }, "energySavingStartDate": {
                        "key": "energySavingStartDate",
                        "operations": []
                    }, "energySavingValue": {
                        "key": "Annual Energy Savings",
                        "operations": []
                    }, "hasEnergySavingType": {
                        "key": "hasEnergySavingType",
                        "operations": []
                    }
                },
            }
        }

        grouped_modules = {
            "building_info": [buildings, building_space, location_info, gross_floor_area, owner,
                              energy_performance_certificate, project, devices, element],
            "emm": [eem, energy_saving]
        }
        return grouped_modules[group]
