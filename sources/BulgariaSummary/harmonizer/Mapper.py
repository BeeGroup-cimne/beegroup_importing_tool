from slugify import slugify

from utils.data_transformations import to_object_property
from utils.rdf_utils.ontology.bigg_classes import Organization, Building, LocationInfo, BuildingSpace, Area, \
    EnergyPerformanceCertificate, BuildingSpaceUseType, AreaType, AreaUnitOfMeasurement, Element, Device, \
    EnergyEfficiencyMeasure, Sensor, EnergySaving
from utils.rdf_utils.ontology.namespaces_definition import Bigg, units, bigg_enums, countries


class Mapper(object):
    def __init__(self, source, namespace):
        self.source = source
        Organization.set_namespace(namespace)
        Building.set_namespace(namespace)
        LocationInfo.set_namespace(namespace)
        BuildingSpace.set_namespace(namespace)
        BuildingSpaceUseType.set_namespace(namespace)
        Area.set_namespace(namespace)
        EnergyPerformanceCertificate.set_namespace(namespace)
        AreaType.set_namespace(namespace)
        AreaUnitOfMeasurement.set_namespace(namespace)
        Element.set_namespace(namespace)
        Device.set_namespace(namespace)
        EnergyEfficiencyMeasure.set_namespace(namespace)
        Sensor.set_namespace(namespace)
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
                    "subject": slugify("bulgaria"),
                    "organizationName": "Bulgaria",
                    "organizationDivisionType": "Department"
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
                    "organizationName": {
                        "key": "building_name",
                        "operations": []
                    }
                }
            },
            "links": {
                "building": {
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
                    "buildingName": {
                        "key": "building_name",
                        "operations": []
                    },
                    "buildingIDFromOrganization": {
                        "key": "subject",
                        "operations": []
                    }
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
                "energy_performance_certificate_before": {
                    "type": Bigg.hasEPC,
                    "link": "epc_subject_before"
                },
                "energy_performance_certificate_after": {
                    "type": Bigg.hasEPC,
                    "link": "epc_subject_after"
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
                "raw": {
                    "hasAddressCountry":
                        to_object_property("732800/", namespace=countries)
                },
                "mapping": {
                    "subject": {
                        "key": "location_subject",
                        "operations": []
                    },
                    "hasAddressCity": {
                        "key": "municipality",
                        "operations": []
                    }
                }
            }
        }

        energy_performance_certificate_before = {
            "name": "energy_performance_certificate_before",
            "class": EnergyPerformanceCertificate,
            "type": {
                "origin": "row"
            },
            "params": {
                "mapping": {
                    "subject": {
                        "key": "epc_subject_before",
                        "operations": []
                    },
                    "energyPerformanceCertificateDateOfAssessment": {
                        "key": "epc_date_before",
                        "operations": []
                    },
                    "energyPerformanceClass": {
                        "key": "epc_energy_class_before",
                        "operations": []
                    },
                    "annualFinalEnergyConsumption": {
                        "key": "annual_energy_consumption_before_total_consumption",
                        "operations": []
                    }
                }
            }
        }

        energy_performance_certificate_after = {
            "name": "energy_performance_certificate_after",
            "class": EnergyPerformanceCertificate,
            "type": {
                "origin": "row"
            },
            "params": {
                "mapping": {
                    "subject": {
                        "key": "epc_subject_after",
                        "operations": []
                    },
                    "energyPerformanceCertificateDateOfAssessment": {
                        "key": "epc_date",
                        "operations": []
                    },
                    "energyPerformanceClass": {
                        "key": "epc_energy_class_after",
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
                    }
                }
            },
            "links": {
                "gross_floor_area": {
                    "type": Bigg.hasArea,
                    "link": "subject"
                },
                "building_space_use_type": {
                    "type": Bigg.hasBuildingSpaceUseType,
                    "link": "subject"
                },
                "element": {
                    "type": Bigg.isAssociatedWithElement,
                    "link": "subject"
                }
            }
        }

        building_space_use_type = {
            "name": "building_space_use_type",
            "class": BuildingSpaceUseType,
            "type": {
                "origin": "row"
            },
            "params": {
                "mapping": {
                    "subject": {
                        "key": "building_space_use_type_subject",
                        "operations": []
                    }
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
                    "hasAreaType": to_object_property("GrossFloorAreaAboveGround", namespace=bigg_enums),
                    "hasAreaUnitOfMeasurement": to_object_property("M2", namespace=units)
                },
                "mapping": {
                    "subject": {
                        "key": "gross_floor_area_subject",
                        "operations": []
                    },
                    "areaValue": {
                        "key": "gross_floor_area",
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

                }
            },
            "links": {
                "device": {
                    "type": Bigg.isObservedByDevice,
                    "link": "subject"
                },
                "energy_efficiency_measurement": {
                    "type": Bigg.isAffectedByMeasure,
                    "link": "subject"
                }
            }
        }

        device = {
            "name": "device",
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

        eem = []
        for i in range(14):
            links = {}

            for j in range(7):
                links.update({
                    f"energy_saving_{i}_{j}": {
                        "type": Bigg.producesSaving,
                        "link": "subject"
                    }
                })

            eem.append({
                "name": f"eem_{i}",
                "class": EnergyEfficiencyMeasure,
                "type": {
                    "origin": "row"
                },
                "params": {
                    "raw": {
                        "hasEnergyEfficiencyMeasureInvestmentCurrency": units["BulgarianLev"],
                        "energyEfficiencyMeasureCurrencyExchangeRate": "0.51",
                        # "hasEnergyEfficiencyMeasureType": to_object_property(f"emm_{i}_type", namespace=bigg_enums),
                    },
                    "mapping": {
                        "subject": {
                            "key": f"subject_eem_{i}",
                            "operations": []
                        },
                        "energyEfficiencyMeasureInvestment": {
                            "key": f"measurement_{i}_Investments",
                            "operations": []
                        }
                    },
                    "links": links
                }

            })

        energy_savings = []

        energy_savings_types = ["Liquid_fuels", "Hard_fuels", "Gas", "Others", "Heat_energy", "Electricity", "Total"]
        hasEnergySavingsType = ['OilSaving', 'CoalSaving', 'GasSaving', 'OtherSavings', 'DistrictHeatingSaving',
                                'GridElectricitySaving', 'TotalEnergySaving']
        for i in range(14):
            for j in range(7):
                energy_savings.append({
                    "name": f"energy_saving_{i}_{j}",
                    "class": EnergySaving,
                    "type": {
                        "origin": "row"
                    },
                    "params": {
                        "raw": {
                            # "hasEnergySavingType": to_object_property(hasEnergySavingsType[j], namespace=bigg_enums)
                        },
                        "mapping": {
                            "subject": {
                                "key": f"energy_saving_{i}_{j}_subject",
                                "operations": []
                            },
                            "energySavingValue": {
                                "key": f"measurement_{i}_{energy_savings_types[j]}",
                                "operations": []
                            },
                            "energySavingStartDate": {
                                "key": f"epc_date_before",
                                "operations": []
                            },
                            "energySavingEndDate": {
                                "key": f"epc_date",
                                "operations": []
                            },
                        }
                    }
                })

        grouped_modules = {
            "all": [organization, building_organization, buildings, building_space,
                    building_space_use_type, gross_floor_area, location_info, energy_performance_certificate_before,
                    energy_performance_certificate_after, element, device
                    ] + eem + energy_savings
        }

        return grouped_modules[group]
