from functools import partial

from slugify import slugify

from utils.data_transformations import building_subject, location_info_subject, building_department_subject, \
    building_space_subject, gross_area_subject
from utils.rdf_utils.big_classes import Organization, Building, LocationInfo, BuildingSpace, Area
from utils.rdf_utils.bigg_definition import Bigg


class Mapper(object):
    def __init__(self, source, namespace):
        self.source = source
        Organization.set_namespace(namespace)
        Building.set_namespace(namespace)
        LocationInfo.set_namespace(namespace)
        BuildingSpace.set_namespace(namespace)
        Area.set_namespace(namespace)

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
                        "key": "subject",
                        "operations": [building_department_subject]
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
                        "key": "subject",
                        "operations": [building_subject]
                    },
                    "buildingUseType": {
                        "key": "type_of_building",
                        "operations": []
                    },
                    "buildingName": {
                        "key": "building_name",
                        "operations": []
                    },
                    "buildingIDFromOrganization": {
                        "key": "subject",
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
                        "key": "subject",
                        "operations": [building_space_subject]
                    }
                }
            },
            "links": {
                "gross_floor_area": {
                    "type": Bigg.hasAreas,
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
                "raw": {
                    "addressCountry": "Bulgaria"
                },
                "mapping": {
                    "subject": {
                        "key": "subject",
                        "operations": [location_info_subject]
                    },
                    "addressCity": {
                        "key": "municipality",
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
                    "areaType": "GrossFloorArea",
                    "areaUnitOfMeasurement": "m2",
                },
                "mapping": {
                    "subject": {
                        "key": "subject",
                        "operations": [partial(gross_area_subject, a_source=self.source)]
                    },
                    "areaValue": {
                        "key": "gross_floor_area",
                        "operations": []
                    }
                }
            }
        }

        grouped_modules = {
            "all": [organization, building_organization, buildings, location_info, building_space, gross_floor_area]
        }

        return grouped_modules[group]
