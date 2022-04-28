from .transform_functions import ref_cadastral
from utils.rdf_utils.ontology.namespaces_definition import Bigg, bigg_enums, units
from utils.rdf_utils.ontology.bigg_classes import Organization, Building, LocationInfo, CadastralInfo, BuildingSpace, \
     Area, Device, BuildingConstructionElement, UtilityPointOfDelivery
from slugify import slugify as slugify
from utils.data_transformations import *

building_type_taxonomy = partial(taxonomy_mapping, taxonomy_file="sources/Gemweb/harmonizer/BuildingUseTypeTaxonomy.xls",
                                 default="Other")

utility_type_taxonomy = partial(taxonomy_mapping, taxonomy_file="sources/Gemweb/harmonizer/EnergyTypeTaxonomy.xls",
                                default="")


class Mapping(object):

    def __init__(self, source, namespace):
        self.source = source
        Organization.set_namespace(namespace)
        Building.set_namespace(namespace)
        LocationInfo.set_namespace(namespace)
        BuildingSpace.set_namespace(namespace)
        CadastralInfo.set_namespace(namespace)
        Area.set_namespace(namespace)
        BuildingConstructionElement.set_namespace(namespace)
        Device.set_namespace(namespace)
        UtilityPointOfDelivery.set_namespace(namespace)

    def get_mappings(self, group):

        building = {
            "name": "building",
            "class": Building,
            "type": {
                "origin": "row"
            },
            "params": {
                "mapping": {
                    "subject": {
                        "key": "codi",
                        "operations": [decode_hbase, id_zfill, building_subject]
                    },
                    "buildingIDFromOrganization": {
                        "key": "codi",
                        "operations": [decode_hbase, id_zfill]
                    },
                    "buildingName": {
                        "key": "nom",
                        "operations": [decode_hbase, ]
                    },
                    # "buildingUseType": {
                    #     "key": "subtipus",
                    #     "operations": [decode_hbase]#, building_type_taxonomy]
                    # },
                    # "buildingOwnership": {
                    #     "key": "responsable",
                    #     "operations": [decode_hbase]
                    # },
                }
            },
            "links": {
                "building_space": {
                    "type": Bigg.hasSpace,
                    "link": "dev_gem_id"
                },
                "location_info": {
                    "type": Bigg.hasLocationInfo,
                    "link": "dev_gem_id"
                },
                "cadastral_info": {
                    "type": Bigg.hasCadastralInfo,
                    "link": "dev_gem_id"
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
                        "key": "codi",
                        "operations": [decode_hbase, id_zfill, location_info_subject]
                    },
                    "hasAddressCountry": {
                        "key": "pais",
                        "operations": [decode_hbase,
                                       partial(fuzzy_dictionary_match,
                                               dictionary="utils/rdf_utils/ontology/dictionaries/countries.ttl",
                                               predicates=['ns1:countryCode'])]
                    },
                    "hasAddressProvince": {
                        "key": "provincia",
                        "operations": [decode_hbase,
                                       partial(fuzzy_dictionary_match,
                                               dictionary="utils/rdf_utils/ontology/dictionaries/province.ttl",
                                               predicates=['ns1:name'])]
                    },
                    "hasAddressCity": {
                        "key": "poblacio",
                        "operations": [decode_hbase,
                                       partial(fuzzy_dictionary_match,
                                               dictionary="utils/rdf_utils/ontology/dictionaries/municipality.ttl",
                                               predicates=['ns1:name'])]
                    },
                    "addressPostalCode": {
                        "key": "codi_postal",
                        "operations": [decode_hbase, ]
                    },
                    "addressStreetName": {
                        "key": "direccio",
                        "operations": [decode_hbase, ]
                    },
                    "addressLongitude": {
                        "key": "longitud",
                        "operations": [decode_hbase, ]
                    },
                    "addressLatitude": {
                        "key": "latitud",
                        "operations": [decode_hbase, ]
                    }
                }
            }
        }

        cadastral_info = {
            "name": "cadastral_info",
            "class": CadastralInfo,
            "type": {
                "origin": "row_split_column",
                "operations": [decode_hbase, ref_cadastral, validate_ref_cadastral],
                "sep": ";",
                "column": "observacionsbuilding",
                "column_mapping": {
                    "subject": [str.strip, cadastral_info_subject],
                    "landCadastralReference": [str.strip]
                }
            },
            "params": {
                "column_mapping": {
                    "subject": "subject",
                    "landCadastralReference": "landCadastralReference"
                },
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
                        "key": "codi",
                        "operations": [decode_hbase, id_zfill, slugify, building_space_subject, ]
                    },
                    "hasBuildingSpaceUseType": {
                        "key": "subtipus",
                        "operations": [decode_hbase, building_type_taxonomy, partial(to_object_property, namespace=bigg_enums)]
                    }
                }
            },
            "links": {
                "gross_floor_area": {
                    "type": Bigg.hasArea,
                    "link": "dev_gem_id"
                },
                "building_element": {
                    "type": Bigg.isAssociatedWithElement,
                    "link": "dev_gem_id"
                },
                "device": {
                    "type": Bigg.isObservedByDevice,
                    "link": "dev_gem_id"
                },
                "utility_point": {
                    "type": Bigg.hasUtilityPointOfDelivery,
                    "link": "dev_gem_id"
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
                        "key": "codi",
                        "operations": [decode_hbase, id_zfill, partial(gross_area_subject, a_source=self.source)]
                    },
                    "areaValue": {
                        "key": "superficie",
                        "operations": [decode_hbase, ]
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
                        "key": "codi",
                        "operations": [decode_hbase, id_zfill, construction_element_subject]
                    }
                }
            }
        }

        utility_point = {
            "name": "utility_point",
            "class": UtilityPointOfDelivery,
            "type": {
                "origin": "row"
            },
            "params": {
                "mapping": {
                    "subject": {
                        "key": "cups",
                        "operations": [decode_hbase, delivery_subject]
                    },
                    "pointOfDeliveryIDFromOrganization": {
                        "key": "cups",
                        "operations": [decode_hbase, ]
                    },
                    "hasUtilityType": {
                        "key": "tipus_submin",
                        "operations": [decode_hbase, utility_type_taxonomy, partial(to_object_property, namespace=bigg_enums)]
                    }
                }
            },
            "links": {
                "device": {
                    "type": Bigg.hasDevice,
                    "link": "dev_gem_id"
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
                "raw": {
                    #"source": "gemweb", segurament no cal posar source, ja que no es de RDF. Afegir despres fora.
                    "hasDeviceType": to_object_property("Meter.EnergyMeter", namespace=bigg_enums)
                },
                "mapping": {
                    "subject": {
                        "key": "dev_gem_id",
                        "operations": [decode_hbase, partial(device_subject, source=self.source)]
                    },
                    "deviceName":  {
                        "key": "cups",
                        "operations": [decode_hbase, ]
                    }
                }
            }
        }

        grouped_modules = {
            "linked": [building, location_info, cadastral_info, building_space,
                       gross_floor_area, building_element, device, utility_point],
            "unlinked": [device]
        }
        return grouped_modules[group]
