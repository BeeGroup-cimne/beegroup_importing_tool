from utils.rdf_utils.ontology.bigg_classes import Building, LocationInfo, BuildingSpace, Area, \
    EnergyPerformanceCertificate, AreaType, AreaUnitOfMeasurement, RenovationProject, BuildingOwnership
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

        grouped_modules = {
            "building_info": [buildings, building_space, location_info, gross_floor_area, owner,
                              energy_performance_certificate, project]
        }
        return grouped_modules[group]
