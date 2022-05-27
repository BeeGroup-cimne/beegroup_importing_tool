from utils.rdf_utils.ontology.bigg_classes import Organization, Building, LocationInfo, BuildingSpace, \
    BuildingSpaceUseType, Area, EnergyPerformanceCertificate, AreaType, AreaUnitOfMeasurement, Element, Device, \
    EnergyEfficiencyMeasure, Sensor, EnergySaving


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
