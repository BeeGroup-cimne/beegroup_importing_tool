from utils.data_transformations import *
from utils.rdf_utils.ontology.namespaces_definition import Bigg, bigg_enums, units, countries
from utils.rdf_utils.ontology.bigg_classes import Organization, Building, LocationInfo, CadastralInfo, BuildingSpace, \
    Area, BuildingConstructionElement



class Mapper(object):
    def __init__(self, source, namespace):
        self.source = source
        Organization.set_namespace(namespace)
        Building.set_namespace(namespace)
        LocationInfo.set_namespace(namespace)
        BuildingSpace.set_namespace(namespace)
        CadastralInfo.set_namespace(namespace)
        Area.set_namespace(namespace)
        BuildingConstructionElement.set_namespace(namespace)

    def get_mappings(self, group):
        organization_organization = {
            "name": "organization_organization",
            "class": Organization,
            "type": {
                "origin": "row_split_column",
                "operations": [],
                "sep": ";",
                "column": "organization_organization",
                "column_mapping": {
                    "subject": [],
                }
            },
            "params": {
                "raw": {
                    "organizationDivisionType": "Organization"
                },
                "column_mapping": {
                    "subject": "subject",
                }
            },
            "links": {
                # "main_organization": {
                #     "type": Bigg.hasSuperOrganization,
                #     "link": "__all__"
                # },
                "building_organization": {
                    "type": Bigg.hasSubOrganization,
                    "link": "Num_Ens_Inventari"
                }
            }
        }

        department_organization = {
            "name": "department_organization",
            "class": Organization,
            "type": {
                "origin": "row_split_column",
                "operations": [],
                "sep": ";",
                "column": "department_organization",
                "column_mapping": {
                    "subject": [],
                }
            },
            "params": {
                "raw": {
                    "organizationDivisionType": "Department"
                },
                "column_mapping": {
                    "subject": "subject",
                }
            },
            "links": {
                # "main_organization": {
                #     "type": Bigg.hasSuperOrganization,
                #     "link": "__all__"
                # },
                "building_organization": {
                    "type": Bigg.hasSubOrganization,
                    "link": "Num_Ens_Inventari"
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
                        "key": "building_organization",
                        "operations": []
                    },
                    "organizationName": {
                        "key": "Espai",
                        "operations": []
                    }
                }
            },
            "links": {
                # "department_organization": {
                #     "type": Bigg.hasSuperOrganization,
                #     "link": "Num_Ens_Inventari",
                #     "fallback": {
                #         "key": "main_organization",
                #         "bidirectional": Bigg.hasSubOrganization
                #     }
                # },
                "building": {
                    "type": Bigg.managesBuilding,
                    "link": "Num_Ens_Inventari"
                }
            }
        }

        building = {
            "name": "building",
            "class": Building,
            "type": {
                "origin": "row"
            },
            "params": {
                "mapping": {
                    "subject": {
                        "key": "building",
                        "operations": []
                    },
                    "buildingIDFromOrganization": {
                        "key": "buildingIDFromOrganization",
                        "operations": []
                    },
                    "buildingName": {
                        "key": "Espai",
                        "operations": []
                    }
                }
            },
            "links": {
                # "building_organization": {
                #     "type": Bigg.pertainsToOrganization,
                #     "link": "Num_Ens_Inventari"
                # },
                "building_space": {
                    "type": Bigg.hasSpace,
                    "link": "Num_Ens_Inventari"
                },
                "location_info": {
                    "type": Bigg.hasLocationInfo,
                    "link": "Num_Ens_Inventari"
                },
                "cadastral_info": {
                    "type": Bigg.hasCadastralInfo,
                    "link": "Num_Ens_Inventari"
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
                        to_object_property("2510769/", namespace=countries),
                    "addressTimeZone": "Europe/Madrid"
                },
                "mapping": {
                    "subject": {
                        "key": "location_info",
                        "operations": []
                    },
                    "hasAddressProvince": {
                        "key": "hasAddressProvince",
                        "operations": []
                    },
                    "hasAddressCity": {
                        "key": "hasAddressCity",
                        "operations": []
                    },
                    "addressPostalCode": {
                        "key": "Codi_postal",
                        "operations": []
                    },
                    "addressStreetNumber": {
                        "key": "Num_via",
                        "operations": []
                    },
                    "addressStreetName": {
                        "key": "Via",
                        "operations": []
                    }
                }
            }
        }

        cadastral_info = {
            "name": "cadastral_info",
            "class": CadastralInfo,
            "type": {
                "origin": "row_split_column",
                "operations": [],
                "sep": ";",
                "column": "cadastral_info",
                "column_mapping": {
                    "subject": [cadastral_info_subject],
                    "landCadastralReference": []
                }
            },
            "params": {
                "column_mapping": {
                    "subject": "subject",
                    "landCadastralReference": "landCadastralReference"
                },
                "mapping": {
                    "landArea": {
                        "key": "Sup_terreny",
                        "operations": []
                    }  # ,
                    # "landType": {
                    #     "key": "Classificacio_sol",
                    #     "operations": [decode_hbase, ]
                    # }
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
                        "key": "building_space",
                        "operations": []
                    },
                    "hasBuildingSpaceUseType": {
                        "key": "hasBuildingSpaceUseType",
                        "operations": []
                    }
                }
            },
            "links": {
                "gross_floor_area": {
                    "type": Bigg.hasArea,
                    "link": "Num_Ens_Inventari"
                },
                "gross_floor_area_above_ground": {
                    "type": Bigg.hasArea,
                    "link": "Num_Ens_Inventari"
                },
                "gross_floor_area_under_ground": {
                    "type": Bigg.hasArea,
                    "link": "Num_Ens_Inventari"
                },
                "building_element": {
                    "type": Bigg.isAssociatedWithElement,
                    "link": "Num_Ens_Inventari"
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
                    "hasAreaType": to_object_property("GrossFloorArea", namespace=bigg_enums),
                    "hasAreaUnitOfMeasurement": to_object_property("M2", namespace=units),
                },
                "mapping": {
                    "subject": {
                        "key": "gross_floor_area",
                        "operations": []
                    },
                    "areaValue": {
                        "key": "Sup_const_total",
                        "operations": []
                    }
                }
            }
        }

        gross_floor_area_above_ground = {
            "name": "gross_floor_area_above_ground",
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
                        "key": "gross_floor_area_above_ground",
                        "operations": []
                    },
                    "areaValue": {
                        "key": "Sup_const_sobre_rasant",
                        "operations": []
                    }
                }
            }
        }

        gross_floor_area_under_ground = {
            "name": "gross_floor_area_under_ground",
            "class": Area,
            "type": {
                "origin": "row"
            },
            "params": {
                "raw": {
                    "hasAreaType": to_object_property("GrossFloorAreaUnderGround", namespace=bigg_enums),
                    "hasAreaUnitOfMeasurement": to_object_property("M2", namespace=units),
                },
                "mapping": {
                    "subject": {
                        "key": "gross_floor_area_under_ground",
                        "operations": []
                    },
                    "areaValue": {
                        "key": "Sup_const_sota rasant",
                        "operations": []
                    }
                }
            }
        }
        building_element = {
            "name": "building_element",
            "class": BuildingConstructionElement,
            "type": {
                "origin": "row"
            },
            "params": {
                "raw": {
                    "hasBuildingConstructionElementType": to_object_property("OtherBuildingConstructionElement",
                                                                             namespace=bigg_enums),
                },
                "mapping": {
                    "subject": {
                        "key": "building_element",
                        "operations": []
                    }
                }
            }
        }
        grouped_modules = {
            "all": [organization_organization, department_organization, building_organization, building, location_info, cadastral_info,
                    building_space, gross_floor_area, gross_floor_area_under_ground, gross_floor_area_above_ground,
                    building_element],
            "buildings": [building_organization, building, location_info, cadastral_info, building_space,
                          gross_floor_area, gross_floor_area_under_ground, gross_floor_area_above_ground,
                          building_element]
        }
        return grouped_modules[group]
