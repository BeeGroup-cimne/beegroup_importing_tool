from slugify import slugify

from sources.Bulgaria.constants import eem_headers, enum_energy_saving_type, \
    enum_energy_efficiency_measurement_type
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

    def generate_energy_efficiency_measurement(self, column, links):
        return {
            "name": f"eem_{column}",
            "class": EnergyEfficiencyMeasure,
            "type": {
                "origin": "row"
            },
            "params": {
                "raw": {
                    "hasEnergyEfficiencyMeasureInvestmentCurrency": units["BulgarianLev"],
                    "energyEfficiencyMeasureCurrencyExchangeRate": "0.51",
                    "hasEnergyEfficiencyMeasureType": to_object_property(
                        enum_energy_efficiency_measurement_type[column],
                        namespace=bigg_enums),
                },
                "mapping": {
                    "subject": {
                        "key": f"eem_{column}_subject",
                        "operations": []
                    },
                    "energyEfficiencyMeasureInvestment": {
                        "key": f"measurement_{column}_Investments",
                        "operations": []
                    }
                },
            },
            "links": links
        }

    def generate_energy_saving(self, column, subcolumn, energy_saving_type, measurement_type):
        if energy_saving_type != 'OtherSavings':
            energy_saving_type = to_object_property(energy_saving_type, namespace=bigg_enums)

        return {
            "name": f"energy_saving_{column}_{subcolumn}",
            "class": EnergySaving,
            "type": {
                "origin": "row"
            },
            "params": {
                "raw": {
                    "hasEnergySavingType": energy_saving_type
                },
                "mapping": {
                    "subject": {
                        "key": f"energy_saving_{column}_{subcolumn}_subject",
                        "operations": []
                    },
                    "energySavingValue": {
                        "key": f"measurement_{column}_{measurement_type}",
                        "operations": []
                    },
                    "energySavingStartDate": {
                        "key": f"epc_date_before",
                        "operations": []
                    },
                    "energySavingEndDate": {
                        "key": f"epc_date",
                        "operations": []
                    }
                }
            }
        }

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
                    "organizationName": self.source,
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
                    "link": "epc_before_subject"
                },
                "energy_performance_certificate_after": {
                    "type": Bigg.hasEPC,
                    "link": "epc_after_subject"
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
                        "key": "epc_before_subject",
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
                        "key": "epc_after_subject",
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
                    # TODO: "hasBuildingSpaceUseType": to_object_property("TAXONOMY_TYPE", namespace=bigg_enums)
                },
                "mapping": {
                    "subject": {
                        "key": "building_space_subject",
                        "operations": []
                    },
                }
            },
            "links": {
                "gross_floor_area": {
                    "type": Bigg.hasArea,
                    "link": "subject"
                },
                "element": {
                    "type": Bigg.isAssociatedWithElement,
                    "link": "subject"
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
                }
            }
        }

        for i in range(len(enum_energy_efficiency_measurement_type)):
            element['links'].update({f"eem_{i}": {
                "type": Bigg.isAffectedByMeasure,
                "link": "subject"}})

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

        energy_saving_list = []
        eem_list = []

        for i in range(len(enum_energy_efficiency_measurement_type)):
            links = {}
            for j in range(len(enum_energy_saving_type)):
                energy_saving_list.append(self.generate_energy_saving(column=i, subcolumn=j,
                                                                      energy_saving_type=enum_energy_saving_type[j],
                                                                      measurement_type=eem_headers[j]))

                links.update({f"energy_saving_{i}_{j}": {"type": Bigg.producesSaving, "link": "subject"}})
            eem_list.append(self.generate_energy_efficiency_measurement(column=i, links=links))

        grouped_modules = {
            "all": [organization, building_organization, buildings, building_space,
                    gross_floor_area, location_info, energy_performance_certificate_before,
                    energy_performance_certificate_after, element, device
                    ] + energy_saving_list + eem_list,
            "test": energy_saving_list + eem_list
        }

        return grouped_modules[group]
