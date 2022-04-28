from rdflib import RDF, Literal, Graph, URIRef
from utils.rdf_utils.ontology.namespaces_definition import *


class BIGGObjects(object):
    __rdf_type__ = "__invalid__"
    __rdf_namespace__ = "__invalid__"

    @classmethod
    def set_namespace(cls, namespace):
        cls.__rdf_namespace__ = namespace

    def __init__(self, subject):
        self.subject = self.__rdf_namespace__[subject]
        if self.__class__ == BIGGObjects.__class__:
            raise NotImplementedError("The BiggObject is abstract")

    def get_graph(self):
        g = Graph()
        g.add((self.subject, RDF.type, self.__rdf_type__))
        for k, v in vars(self).items():
            if k != "subject" and v:
                if isinstance(v, URIRef):
                    g.add((self.subject, Bigg[k], v))
                else:
                    g.add((self.subject, Bigg[k], Literal(v)))
        return g


class AnalyticsResults(BIGGObjects):
    __rdf_type__ = Bigg.AnalyticsResults

    def __init__(self, subject, ):
        super().__init__(subject)


class Area(BIGGObjects):
    __rdf_type__ = Bigg.Area

    def __init__(self, subject, areaValue=None, hasAreaType=None, hasAreaUnitOfMeasurement=None):
        super().__init__(subject)
        self.areaValue = areaValue
        self.hasAreaType = hasAreaType
        self.hasAreaUnitOfMeasurement = hasAreaUnitOfMeasurement


class AreaType(BIGGObjects):
    __rdf_type__ = Bigg.AreaType

    def __init__(self, subject, ):
        super().__init__(subject)


class AreaUnitOfMeasurement(BIGGObjects):
    __rdf_type__ = Bigg.AreaUnitOfMeasurement

    def __init__(self, subject, ):
        super().__init__(subject)


class Baseline(BIGGObjects):
    __rdf_type__ = Bigg.Baseline

    def __init__(self, subject, baselineDefinition=None, baselinePerimeter=None, baselineNonAdjustedValue=None,
                 baselineAdjustedValue=None, baselineUnit=None, hasBaselineInfluenceFactor=None):
        super().__init__(subject)
        self.baselineDefinition = baselineDefinition
        self.baselinePerimeter = baselinePerimeter
        self.baselineNonAdjustedValue = baselineNonAdjustedValue
        self.baselineAdjustedValue = baselineAdjustedValue
        self.baselineUnit = baselineUnit
        self.hasBaselineInfluenceFactor = hasBaselineInfluenceFactor


class BaselineInfluenceFactor(BIGGObjects):
    __rdf_type__ = Bigg.BaselineInfluenceFactor

    def __init__(self, subject, ):
        super().__init__(subject)


class Benchmarking(BIGGObjects):
    __rdf_type__ = Bigg.Benchmarking

    def __init__(self, subject, ):
        super().__init__(subject)


class Building(BIGGObjects):
    __rdf_type__ = Bigg.Building

    def __init__(self, subject, buildingIDFromOrganization=None, buildingName=None, buildingConstructionYear=None,
                 buildingOpeningHour=None, buildingClosingHour=None, hasBuildingConstructionType=None,
                 hasBuildingOwnership=None, pertainsToOrganization=None, hasCadastralInfo=None, hasLocationInfo=None,
                 hasProject=None, hasSpace=None, hasResult=None, hasEPC=None):
        super().__init__(subject)
        self.buildingIDFromOrganization = buildingIDFromOrganization
        self.buildingName = buildingName
        self.buildingConstructionYear = buildingConstructionYear
        self.buildingOpeningHour = buildingOpeningHour
        self.buildingClosingHour = buildingClosingHour
        self.hasBuildingConstructionType = hasBuildingConstructionType
        self.hasBuildingOwnership = hasBuildingOwnership
        self.pertainsToOrganization = pertainsToOrganization
        self.hasCadastralInfo = hasCadastralInfo
        self.hasLocationInfo = hasLocationInfo
        self.hasProject = hasProject
        self.hasSpace = hasSpace
        self.hasResult = hasResult
        self.hasEPC = hasEPC


class BuildingConstructionType(BIGGObjects):
    __rdf_type__ = Bigg.BuildingConstructionType

    def __init__(self, subject, ):
        super().__init__(subject)


class BuildingOwnership(BIGGObjects):
    __rdf_type__ = Bigg.BuildingOwnership

    def __init__(self, subject, ):
        super().__init__(subject)


class BuildingConstructionElement(BIGGObjects):
    __rdf_type__ = Bigg.BuildingConstructionElement

    def __init__(self, subject, hasBuildingConstructionElementType=None):
        super().__init__(subject)
        self.hasBuildingConstructionElementType = hasBuildingConstructionElementType


class BuildingConstructionElementType(BIGGObjects):
    __rdf_type__ = Bigg.BuildingConstructionElementType

    def __init__(self, subject, ):
        super().__init__(subject)


class BuildingElement(BIGGObjects):
    __rdf_type__ = Bigg.BuildingElement

    def __init__(self, subject, buildingElementIDFromOrganization=None, buildingElementState=None,
                 buildingElementPurchaseDate=None, buildingElementInstallationDate=None, buildingElementBrand=None,
                 buildingElementModel=None, buildingElementSerialNumber=None, buildingElementManufacturer=None,
                 buildingElementManufactureDate=None):
        super().__init__(subject)
        self.buildingElementIDFromOrganization = buildingElementIDFromOrganization
        self.buildingElementState = buildingElementState
        self.buildingElementPurchaseDate = buildingElementPurchaseDate
        self.buildingElementInstallationDate = buildingElementInstallationDate
        self.buildingElementBrand = buildingElementBrand
        self.buildingElementModel = buildingElementModel
        self.buildingElementSerialNumber = buildingElementSerialNumber
        self.buildingElementManufacturer = buildingElementManufacturer
        self.buildingElementManufactureDate = buildingElementManufactureDate


class BuildingSpace(BIGGObjects):
    __rdf_type__ = Bigg.BuildingSpace

    def __init__(self, subject, builidingSpaceIDFromOrganization=None, buildingSpaceName=None,
                 hasBuildingSpaceUseType=None, hasResult=None, hasIndoorQualityPerception=None, hasArea=None,
                 containsElement=None, isAssociatedWithElement=None, isObservedByDevice=None, hasDeviceAggregator=None,
                 containsZone=None, hasSubSpace=None, hasOccupancyProfile=None):
        super().__init__(subject)
        self.builidingSpaceIDFromOrganization = builidingSpaceIDFromOrganization
        self.buildingSpaceName = buildingSpaceName
        self.hasBuildingSpaceUseType = hasBuildingSpaceUseType
        self.hasResult = hasResult
        self.hasIndoorQualityPerception = hasIndoorQualityPerception
        self.hasArea = hasArea
        self.containsElement = containsElement
        self.isAssociatedWithElement = isAssociatedWithElement
        self.isObservedByDevice = isObservedByDevice
        self.hasDeviceAggregator = hasDeviceAggregator
        self.containsZone = containsZone
        self.hasSubSpace = hasSubSpace
        self.hasOccupancyProfile = hasOccupancyProfile


class BuildingSpaceUseType(BIGGObjects):
    __rdf_type__ = Bigg.BuildingSpaceUseType

    def __init__(self, subject, ):
        super().__init__(subject)


class BuildingSystemElement(BIGGObjects):
    __rdf_type__ = Bigg.BuildingSystemElement

    def __init__(self, subject, buildingSystemElementMinOutput=None, buildingSystemElementMaxOutput=None,
                 buildingSystemElementEfficiency=None, hasBuildingSystemElementType=None):
        super().__init__(subject)
        self.buildingSystemElementMinOutput = buildingSystemElementMinOutput
        self.buildingSystemElementMaxOutput = buildingSystemElementMaxOutput
        self.buildingSystemElementEfficiency = buildingSystemElementEfficiency
        self.hasBuildingSystemElementType = hasBuildingSystemElementType


class BuildingSystemElementType(BIGGObjects):
    __rdf_type__ = Bigg.BuildingSystemElementType

    def __init__(self, subject, ):
        super().__init__(subject)


class CadastralInfo(BIGGObjects):
    __rdf_type__ = Bigg.CadastralInfo

    def __init__(self, subject, landCadastralReference=None, landGeometry=None, landArea=None, landGraphicalArea=None,
                 propertyClass=None, hasLandType=None):
        super().__init__(subject)
        self.landCadastralReference = landCadastralReference
        self.landGeometry = landGeometry
        self.landArea = landArea
        self.landGraphicalArea = landGraphicalArea
        self.propertyClass = propertyClass
        self.hasLandType = hasLandType


class LandType(BIGGObjects):
    __rdf_type__ = Bigg.LandType

    def __init__(self, subject, ):
        super().__init__(subject)


class EnergyPerformanceContract(BIGGObjects):
    __rdf_type__ = Bigg.EnergyPerformanceContract

    def __init__(self, subject, contractID=None, contractName=None, contractPerimeter=None, contractStartDate=None,
                 contractEndDate=None, hasObjective=None):
        super().__init__(subject)
        self.contractID = contractID
        self.contractName = contractName
        self.contractPerimeter = contractPerimeter
        self.contractStartDate = contractStartDate
        self.contractEndDate = contractEndDate
        self.hasObjective = hasObjective


class ContractObjective(BIGGObjects):
    __rdf_type__ = Bigg.ContractObjective

    def __init__(self, subject, objectiveID=None, objectiveName=None, objectiveDescription=None,
                 objectiveTargetValue=None, objectiveDeadline=None, hasObjectiveTargetType=None,
                 hasObjectiveTargetValueUnit=None, isConnectedToEnergySaving=None):
        super().__init__(subject)
        self.objectiveID = objectiveID
        self.objectiveName = objectiveName
        self.objectiveDescription = objectiveDescription
        self.objectiveTargetValue = objectiveTargetValue
        self.objectiveDeadline = objectiveDeadline
        self.hasObjectiveTargetType = hasObjectiveTargetType
        self.hasObjectiveTargetValueUnit = hasObjectiveTargetValueUnit
        self.isConnectedToEnergySaving = isConnectedToEnergySaving


class ObjectiveTargetType(BIGGObjects):
    __rdf_type__ = Bigg.ObjectiveTargetType

    def __init__(self, subject, ):
        super().__init__(subject)


class ObjectiveTargetValueUnit(BIGGObjects):
    __rdf_type__ = Bigg.ObjectiveTargetValueUnit

    def __init__(self, subject, ):
        super().__init__(subject)


class CO2EmissionsFactor(BIGGObjects):
    __rdf_type__ = Bigg.CO2EmissionsFactor

    def __init__(self, subject, gridCO2EmissionsFactor=None, gridCO2EmissionsFactorStart=None,
                 gridCO2EmissionsFactorEnd=None):
        super().__init__(subject)
        self.gridCO2EmissionsFactor = gridCO2EmissionsFactor
        self.gridCO2EmissionsFactorStart = gridCO2EmissionsFactorStart
        self.gridCO2EmissionsFactorEnd = gridCO2EmissionsFactorEnd


class Device(BIGGObjects):
    __rdf_type__ = Bigg.Device

    def __init__(self, subject, deviceIDFromOrganization=None, deviceName=None, deviceManufacturer=None,
                 deviceModel=None, deviceNumberOfOutputs=None, deviceOperatingSystem=None,
                 deviceLicenceVersionNumber=None, hasDeviceType=None, hasDeviceInputSignalType=None,
                 hasDeviceInputProtocol=None, observesSpace=None, observesElement=None, hasUtilityPointOfDelivery=None,
                 hasSensor=None, hasDeviceHistory=None, hasState=None, isInWeatherStation=None,
                 isPartOfDeviceAggregator=None):
        super().__init__(subject)
        self.deviceIDFromOrganization = deviceIDFromOrganization
        self.deviceName = deviceName
        self.deviceManufacturer = deviceManufacturer
        self.deviceModel = deviceModel
        self.deviceNumberOfOutputs = deviceNumberOfOutputs
        self.deviceOperatingSystem = deviceOperatingSystem
        self.deviceLicenceVersionNumber = deviceLicenceVersionNumber
        self.hasDeviceType = hasDeviceType
        self.hasDeviceInputSignalType = hasDeviceInputSignalType
        self.hasDeviceInputProtocol = hasDeviceInputProtocol
        self.observesSpace = observesSpace
        self.observesElement = observesElement
        self.hasUtilityPointOfDelivery = hasUtilityPointOfDelivery
        self.hasSensor = hasSensor
        self.hasDeviceHistory = hasDeviceHistory
        self.hasState = hasState
        self.isInWeatherStation = isInWeatherStation
        self.isPartOfDeviceAggregator = isPartOfDeviceAggregator


class DeviceType(BIGGObjects):
    __rdf_type__ = Bigg.DeviceType

    def __init__(self, subject, ):
        super().__init__(subject)


class DeviceInputSignalType(BIGGObjects):
    __rdf_type__ = Bigg.DeviceInputSignalType

    def __init__(self, subject, ):
        super().__init__(subject)


class DeviceInputProtocol(BIGGObjects):
    __rdf_type__ = Bigg.DeviceInputProtocol

    def __init__(self, subject, ):
        super().__init__(subject)


class DeviceHistory(BIGGObjects):
    __rdf_type__ = Bigg.DeviceHistory

    def __init__(self, subject, deviceSerialNumber=None, deviceManufactureDate=None, deviceInstallationDate=None,
                 deviceRemovalDate=None, deviceThresholdValue=None):
        super().__init__(subject)
        self.deviceSerialNumber = deviceSerialNumber
        self.deviceManufactureDate = deviceManufactureDate
        self.deviceInstallationDate = deviceInstallationDate
        self.deviceRemovalDate = deviceRemovalDate
        self.deviceThresholdValue = deviceThresholdValue


class Element(BIGGObjects):
    __rdf_type__ = Bigg.Element

    def __init__(self, subject, isContainedInSpace=None, isAssociatedWithSpace=None, isObservedByDevice=None,
                 isAffectedByMeasure=None, isSubjectToMaintenance=None, isContainedInSystem=None, hasSubElement=None):
        super().__init__(subject)
        self.isContainedInSpace = isContainedInSpace
        self.isAssociatedWithSpace = isAssociatedWithSpace
        self.isObservedByDevice = isObservedByDevice
        self.isAffectedByMeasure = isAffectedByMeasure
        self.isSubjectToMaintenance = isSubjectToMaintenance
        self.isContainedInSystem = isContainedInSystem
        self.hasSubElement = hasSubElement


class EnergyEfficiencyMeasure(BIGGObjects):
    __rdf_type__ = Bigg.EnergyEfficiencyMeasure

    def __init__(self, subject, energyEfficiencyMeasureID=None, energyEfficiencyMeasureLifetime=None,
                 energyEfficiencyMeasureDescription=None, shareOfAffectedElement=None,
                 energyEfficiencyMeasureOperationalDate=None, energyEfficiencyMeasureInvestment=None,
                 energyEfficiencyMeasureCurrencyExchangeRate=None, energyEfficiencyMeasureSavingsToInvestmentRatio=None,
                 energySourcePriceEscalationRate=None, energyEfficiencyMeasureFinancialSavings=None,
                 energyEfficiencyMeasureCO2Reduction=None, hasEnergyEfficiencyMeasureType=None,
                 hasEnergyEfficiencyMeasureInvestmentCurrency=None, affectsElement=None, producesSaving=None,
                 producesNonEnergyBenefit=None):
        super().__init__(subject)
        self.energyEfficiencyMeasureID = energyEfficiencyMeasureID
        self.energyEfficiencyMeasureLifetime = energyEfficiencyMeasureLifetime
        self.energyEfficiencyMeasureDescription = energyEfficiencyMeasureDescription
        self.shareOfAffectedElement = shareOfAffectedElement
        self.energyEfficiencyMeasureOperationalDate = energyEfficiencyMeasureOperationalDate
        self.energyEfficiencyMeasureInvestment = energyEfficiencyMeasureInvestment
        self.energyEfficiencyMeasureCurrencyExchangeRate = energyEfficiencyMeasureCurrencyExchangeRate
        self.energyEfficiencyMeasureSavingsToInvestmentRatio = energyEfficiencyMeasureSavingsToInvestmentRatio
        self.energySourcePriceEscalationRate = energySourcePriceEscalationRate
        self.energyEfficiencyMeasureFinancialSavings = energyEfficiencyMeasureFinancialSavings
        self.energyEfficiencyMeasureCO2Reduction = energyEfficiencyMeasureCO2Reduction
        self.hasEnergyEfficiencyMeasureType = hasEnergyEfficiencyMeasureType
        self.hasEnergyEfficiencyMeasureInvestmentCurrency = hasEnergyEfficiencyMeasureInvestmentCurrency
        self.affectsElement = affectsElement
        self.producesSaving = producesSaving
        self.producesNonEnergyBenefit = producesNonEnergyBenefit


class EnergyEfficiencyMeasureType(BIGGObjects):
    __rdf_type__ = Bigg.EnergyEfficiencyMeasureType

    def __init__(self, subject, ):
        super().__init__(subject)


class EnergyEfficiencyMeasureInvestmentCurrency(BIGGObjects):
    __rdf_type__ = Bigg.EnergyEfficiencyMeasureInvestmentCurrency

    def __init__(self, subject, ):
        super().__init__(subject)


class EnergyPerformanceCertificate(BIGGObjects):
    __rdf_type__ = Bigg.EnergyPerformanceCertificate

    def __init__(self, subject, energyPerformanceCertificateReferenceNumber=None,
                 energyPerformanceCertificateDateOfAssessment=None,
                 energyPerformanceCertificateDateOfCertification=None, energyPerformanceCertificationTool=None,
                 energyPerformanceProcedureType=None, energyPerformanceCertificationMotivation=None,
                 energyPerformanceClass=None, annualPrimaryEnergyConsumption=None, CO2EmissionsClass=None,
                 annualCO2Emissions=None, annualFinalEnergyConsumption=None, annualEnergyCost=None,
                 heatingCO2EmissionsClass=None, annualHeatingCO2Emissions=None, coolingCO2EmissionsClass=None,
                 annualCoolingCO2Emissions=None, hotWaterCO2EmissionsClass=None, annualHotWaterCO2Emissions=None,
                 lightingCO2EmissionsClass=None, annualLightingCO2Emissions=None, heatingPrimaryEnergyClass=None,
                 annualHeatingPrimaryEnergyConsumption=None, coolingPrimaryEnergyClass=None,
                 annualCoolingPrimaryEnergyConsumption=None, hotWaterPrimaryEnergyClass=None,
                 annualHotWaterPrimaryEnergyConsumption=None, lightingPrimaryEnergyClass=None,
                 annualLightingPrimaryEnergyConsumption=None, heatingEnergyDemandClass=None,
                 annualHeatingEnergyDemand=None, coolingEnergyDemandClass=None, annualCoolingEnergyDemand=None,
                 hasAdditionalInfo=None):
        super().__init__(subject)
        self.energyPerformanceCertificateReferenceNumber = energyPerformanceCertificateReferenceNumber
        self.energyPerformanceCertificateDateOfAssessment = energyPerformanceCertificateDateOfAssessment
        self.energyPerformanceCertificateDateOfCertification = energyPerformanceCertificateDateOfCertification
        self.energyPerformanceCertificationTool = energyPerformanceCertificationTool
        self.energyPerformanceProcedureType = energyPerformanceProcedureType
        self.energyPerformanceCertificationMotivation = energyPerformanceCertificationMotivation
        self.energyPerformanceClass = energyPerformanceClass
        self.annualPrimaryEnergyConsumption = annualPrimaryEnergyConsumption
        self.CO2EmissionsClass = CO2EmissionsClass
        self.annualCO2Emissions = annualCO2Emissions
        self.annualFinalEnergyConsumption = annualFinalEnergyConsumption
        self.annualEnergyCost = annualEnergyCost
        self.heatingCO2EmissionsClass = heatingCO2EmissionsClass
        self.annualHeatingCO2Emissions = annualHeatingCO2Emissions
        self.coolingCO2EmissionsClass = coolingCO2EmissionsClass
        self.annualCoolingCO2Emissions = annualCoolingCO2Emissions
        self.hotWaterCO2EmissionsClass = hotWaterCO2EmissionsClass
        self.annualHotWaterCO2Emissions = annualHotWaterCO2Emissions
        self.lightingCO2EmissionsClass = lightingCO2EmissionsClass
        self.annualLightingCO2Emissions = annualLightingCO2Emissions
        self.heatingPrimaryEnergyClass = heatingPrimaryEnergyClass
        self.annualHeatingPrimaryEnergyConsumption = annualHeatingPrimaryEnergyConsumption
        self.coolingPrimaryEnergyClass = coolingPrimaryEnergyClass
        self.annualCoolingPrimaryEnergyConsumption = annualCoolingPrimaryEnergyConsumption
        self.hotWaterPrimaryEnergyClass = hotWaterPrimaryEnergyClass
        self.annualHotWaterPrimaryEnergyConsumption = annualHotWaterPrimaryEnergyConsumption
        self.lightingPrimaryEnergyClass = lightingPrimaryEnergyClass
        self.annualLightingPrimaryEnergyConsumption = annualLightingPrimaryEnergyConsumption
        self.heatingEnergyDemandClass = heatingEnergyDemandClass
        self.annualHeatingEnergyDemand = annualHeatingEnergyDemand
        self.coolingEnergyDemandClass = coolingEnergyDemandClass
        self.annualCoolingEnergyDemand = annualCoolingEnergyDemand
        self.hasAdditionalInfo = hasAdditionalInfo


class EnergyPerformanceCertificateAdditionalInfo(BIGGObjects):
    __rdf_type__ = Bigg.EnergyPerformanceCertificateAdditionalInfo

    def __init__(self, subject, electricVehicleChargerPresence=None, solarThermalSystemPresence=None,
                 solarPVSystemPresence=None, biomassSystemPresence=None, geothermalSystemPresence=None,
                 districtHeatinOrCoolingConnection=None, buildingTecnicalInspectionCode=None,
                 averageFacadeTransmittance=None, averageWindowsTransmittance=None,
                 regulationValueForFacadeTransmittance=None, regulationValueForWindowsTransmittance=None,
                 constructionRegulation=None):
        super().__init__(subject)
        self.electricVehicleChargerPresence = electricVehicleChargerPresence
        self.solarThermalSystemPresence = solarThermalSystemPresence
        self.solarPVSystemPresence = solarPVSystemPresence
        self.biomassSystemPresence = biomassSystemPresence
        self.geothermalSystemPresence = geothermalSystemPresence
        self.districtHeatinOrCoolingConnection = districtHeatinOrCoolingConnection
        self.buildingTecnicalInspectionCode = buildingTecnicalInspectionCode
        self.averageFacadeTransmittance = averageFacadeTransmittance
        self.averageWindowsTransmittance = averageWindowsTransmittance
        self.regulationValueForFacadeTransmittance = regulationValueForFacadeTransmittance
        self.regulationValueForWindowsTransmittance = regulationValueForWindowsTransmittance
        self.constructionRegulation = constructionRegulation


class Contract(BIGGObjects):
    __rdf_type__ = Bigg.Contract

    def __init__(self, subject, ):
        super().__init__(subject)


class EnergySaving(BIGGObjects):
    __rdf_type__ = Bigg.EnergySaving

    def __init__(self, subject, energySavingValue=None, energySavingStartDate=None, energySavingEndDate=None,
                 energySavingIndependentlyVerified=None, hasEnergySavingType=None,
                 hasEnergySavingVerificationSource=None, influencesObjective=None):
        super().__init__(subject)
        self.energySavingValue = energySavingValue
        self.energySavingStartDate = energySavingStartDate
        self.energySavingEndDate = energySavingEndDate
        self.energySavingIndependentlyVerified = energySavingIndependentlyVerified
        self.hasEnergySavingType = hasEnergySavingType
        self.hasEnergySavingVerificationSource = hasEnergySavingVerificationSource
        self.influencesObjective = influencesObjective


class EnergySavingType(BIGGObjects):
    __rdf_type__ = Bigg.EnergySavingType

    def __init__(self, subject, ):
        super().__init__(subject)


class EnergySavingVerificationSource(BIGGObjects):
    __rdf_type__ = Bigg.EnergySavingVerificationSource

    def __init__(self, subject, ):
        super().__init__(subject)


class Group(BIGGObjects):
    __rdf_type__ = Bigg.Group

    def __init__(self, subject, groupID=None, groupName=None, isLinkedWithGroup=None):
        super().__init__(subject)
        self.groupID = groupID
        self.groupName = groupName
        self.isLinkedWithGroup = isLinkedWithGroup


class IndoorQualityPerception(BIGGObjects):
    __rdf_type__ = Bigg.IndoorQualityPerception

    def __init__(self, subject, indoorQualityEvaluationValidityStartDate=None,
                 indoorQualityEvaluationValidityEndDate=None, hasIndoorQualityUserPerception=None):
        super().__init__(subject)
        self.indoorQualityEvaluationValidityStartDate = indoorQualityEvaluationValidityStartDate
        self.indoorQualityEvaluationValidityEndDate = indoorQualityEvaluationValidityEndDate
        self.hasIndoorQualityUserPerception = hasIndoorQualityUserPerception


class IndoorQualityUserPerception(BIGGObjects):
    __rdf_type__ = Bigg.IndoorQualityUserPerception

    def __init__(self, subject, ):
        super().__init__(subject)


class LocationInfo(BIGGObjects):
    __rdf_type__ = Bigg.LocationInfo

    def __init__(self, subject, addressPostalCode=None, addressStreetName=None, addressStreetNumber=None,
                 addressLatitude=None, addressLongitude=None, addressAltitude=None, hasAddressCountry=None,
                 hasAddressProvince=None, hasAddressCity=None, hasAddressClimateZone=None):
        super().__init__(subject)
        self.addressPostalCode = addressPostalCode
        self.addressStreetName = addressStreetName
        self.addressStreetNumber = addressStreetNumber
        self.addressLatitude = addressLatitude
        self.addressLongitude = addressLongitude
        self.addressAltitude = addressAltitude
        self.hasAddressCountry = hasAddressCountry
        self.hasAddressProvince = hasAddressProvince
        self.hasAddressCity = hasAddressCity
        self.hasAddressClimateZone = hasAddressClimateZone


class AddressCountry(BIGGObjects):
    __rdf_type__ = Bigg.AddressCountry

    def __init__(self, subject, ):
        super().__init__(subject)


class AddressProvince(BIGGObjects):
    __rdf_type__ = Bigg.AddressProvince

    def __init__(self, subject, ):
        super().__init__(subject)


class AddressCity(BIGGObjects):
    __rdf_type__ = Bigg.AddressCity

    def __init__(self, subject, ):
        super().__init__(subject)


class AddressClimateZone(BIGGObjects):
    __rdf_type__ = Bigg.AddressClimateZone

    def __init__(self, subject, ):
        super().__init__(subject)


class MaintenanceAction(BIGGObjects):
    __rdf_type__ = Bigg.MaintenanceAction

    def __init__(self, subject, maintenanceActionID=None, maintenanceActionDate=None, maintenanceActionName=None,
                 maintenanceActionDescription=None, maintenanceActionIsPeriodic=None, maintenanceActionFrequency=None,
                 hasMaintenanceActionType=None, maintainsElement=None):
        super().__init__(subject)
        self.maintenanceActionID = maintenanceActionID
        self.maintenanceActionDate = maintenanceActionDate
        self.maintenanceActionName = maintenanceActionName
        self.maintenanceActionDescription = maintenanceActionDescription
        self.maintenanceActionIsPeriodic = maintenanceActionIsPeriodic
        self.maintenanceActionFrequency = maintenanceActionFrequency
        self.hasMaintenanceActionType = hasMaintenanceActionType
        self.maintainsElement = maintainsElement


class MaintenanceActionType(BIGGObjects):
    __rdf_type__ = Bigg.MaintenanceActionType

    def __init__(self, subject, ):
        super().__init__(subject)


class Measurement(BIGGObjects):
    __rdf_type__ = Bigg.Measurement

    def __init__(self, subject, value=None, start=None, end=None, isReal=None):
        super().__init__(subject)
        self.value = value
        self.start = start
        self.end = end
        self.isReal = isReal


class Sensor(BIGGObjects):
    __rdf_type__ = Bigg.Sensor

    def __init__(self, subject, measurementDescription=None, sensorIsCumulative=None, sensorIsOnChange=None,
                 sensorFrequency=None, sensorTimeAggregationFunction=None, sensorProperty=None, sensorStart=None,
                 sensorEnd=None, hasMeasuredProperty=None, hasMeasurementUnit=None, hasSensorReadingType=None,
                 hasSensorEstimationMethod=None, hasOutputSignalType=None, hasOutputProtocol=None, hasMeasurement=None):
        super().__init__(subject)
        self.measurementDescription = measurementDescription
        self.sensorIsCumulative = sensorIsCumulative
        self.sensorIsOnChange = sensorIsOnChange
        self.sensorFrequency = sensorFrequency
        self.sensorTimeAggregationFunction = sensorTimeAggregationFunction
        self.sensorProperty = sensorProperty
        self.sensorStart = sensorStart
        self.sensorEnd = sensorEnd
        self.hasMeasuredProperty = hasMeasuredProperty
        self.hasMeasurementUnit = hasMeasurementUnit
        self.hasSensorReadingType = hasSensorReadingType
        self.hasSensorEstimationMethod = hasSensorEstimationMethod
        self.hasOutputSignalType = hasOutputSignalType
        self.hasOutputProtocol = hasOutputProtocol
        self.hasMeasurement = hasMeasurement


class MeasuredProperty(BIGGObjects):
    __rdf_type__ = Bigg.MeasuredProperty

    def __init__(self, subject, ):
        super().__init__(subject)


class MeasurementUnit(BIGGObjects):
    __rdf_type__ = Bigg.MeasurementUnit

    def __init__(self, subject, ):
        super().__init__(subject)


class SensorReadingType(BIGGObjects):
    __rdf_type__ = Bigg.SensorReadingType

    def __init__(self, subject, ):
        super().__init__(subject)


class SensorEstimationMethod(BIGGObjects):
    __rdf_type__ = Bigg.SensorEstimationMethod

    def __init__(self, subject, ):
        super().__init__(subject)


class OutputSignalType(BIGGObjects):
    __rdf_type__ = Bigg.OutputSignalType

    def __init__(self, subject, ):
        super().__init__(subject)


class OutputProtocol(BIGGObjects):
    __rdf_type__ = Bigg.OutputProtocol

    def __init__(self, subject, ):
        super().__init__(subject)


class DeviceAggregator(BIGGObjects):
    __rdf_type__ = Bigg.DeviceAggregator

    def __init__(self, subject, deviceAggregatorFormula=None, deviceAggregatorName=None, deviceAggregatorFrequency=None,
                 deviceAggregatorTimeAggregationFunction=None, hasDeviceAggregatorProperty=None, hasResult=None,
                 isInSpace=None, includesDevice=None):
        super().__init__(subject)
        self.deviceAggregatorFormula = deviceAggregatorFormula
        self.deviceAggregatorName = deviceAggregatorName
        self.deviceAggregatorFrequency = deviceAggregatorFrequency
        self.deviceAggregatorTimeAggregationFunction = deviceAggregatorTimeAggregationFunction
        self.hasDeviceAggregatorProperty = hasDeviceAggregatorProperty
        self.hasResult = hasResult
        self.isInSpace = isInSpace
        self.includesDevice = includesDevice


class DeviceAggregatorProperty(BIGGObjects):
    __rdf_type__ = Bigg.DeviceAggregatorProperty

    def __init__(self, subject, ):
        super().__init__(subject)


class NonEnergyBenefit(BIGGObjects):
    __rdf_type__ = Bigg.NonEnergyBenefit

    def __init__(self, subject, nonEnergyBenefitImpactValueVerifiedAndMeasured=None,
                 nonEnergyBenefitImpactVerificationMethod=None, nonEnergyBenefitImpactValue=None,
                 nonEnergyBenefitImpactValueDescription=None, hasNonEnergyBenefitType=None,
                 hasNonEnergyBenefitImpactEvaluation=None, hasNonEnergyBenefitImpactValueUnit=None):
        super().__init__(subject)
        self.nonEnergyBenefitImpactValueVerifiedAndMeasured = nonEnergyBenefitImpactValueVerifiedAndMeasured
        self.nonEnergyBenefitImpactVerificationMethod = nonEnergyBenefitImpactVerificationMethod
        self.nonEnergyBenefitImpactValue = nonEnergyBenefitImpactValue
        self.nonEnergyBenefitImpactValueDescription = nonEnergyBenefitImpactValueDescription
        self.hasNonEnergyBenefitType = hasNonEnergyBenefitType
        self.hasNonEnergyBenefitImpactEvaluation = hasNonEnergyBenefitImpactEvaluation
        self.hasNonEnergyBenefitImpactValueUnit = hasNonEnergyBenefitImpactValueUnit


class NonEnergyBenefitType(BIGGObjects):
    __rdf_type__ = Bigg.NonEnergyBenefitType

    def __init__(self, subject, ):
        super().__init__(subject)


class NonEnergyBenefitImpactEvaluation(BIGGObjects):
    __rdf_type__ = Bigg.NonEnergyBenefitImpactEvaluation

    def __init__(self, subject, ):
        super().__init__(subject)


class NonEnergyBenefitImpactValueUnit(BIGGObjects):
    __rdf_type__ = Bigg.NonEnergyBenefitImpactValueUnit

    def __init__(self, subject, ):
        super().__init__(subject)


class OccupancyProfile(BIGGObjects):
    __rdf_type__ = Bigg.OccupancyProfile

    def __init__(self, subject, occupancyProfileValidityStartDate=None, occupancyProfileValidityEndDate=None,
                 occupancyNumberOfOccupants=None, occupancyVacationDates=None):
        super().__init__(subject)
        self.occupancyProfileValidityStartDate = occupancyProfileValidityStartDate
        self.occupancyProfileValidityEndDate = occupancyProfileValidityEndDate
        self.occupancyNumberOfOccupants = occupancyNumberOfOccupants
        self.occupancyVacationDates = occupancyVacationDates


class Organization(BIGGObjects):
    __rdf_type__ = Bigg.Organization

    def __init__(self, subject, organizationID=None, organizationName=None, organizationLocalVAT=None,
                 organizationDivisionType=None, organizationContactPersonName=None, organizationEmail=None,
                 organizationTelephoneNumber=None, hasOrganizationType=None, hasSubOrganization=None,
                 isManagedByPerson=None, buysContract=None, providesContract=None, managesBuilding=None):
        super().__init__(subject)
        self.organizationID = organizationID
        self.organizationName = organizationName
        self.organizationLocalVAT = organizationLocalVAT
        self.organizationDivisionType = organizationDivisionType
        self.organizationContactPersonName = organizationContactPersonName
        self.organizationEmail = organizationEmail
        self.organizationTelephoneNumber = organizationTelephoneNumber
        self.hasOrganizationType = hasOrganizationType
        self.hasSubOrganization = hasSubOrganization
        self.isManagedByPerson = isManagedByPerson
        self.buysContract = buysContract
        self.providesContract = providesContract
        self.managesBuilding = managesBuilding


class OrganizationType(BIGGObjects):
    __rdf_type__ = Bigg.OrganizationType

    def __init__(self, subject, ):
        super().__init__(subject)


class Person(BIGGObjects):
    __rdf_type__ = Bigg.Person

    def __init__(self, subject, userID=None, userName=None, userEmail=None, userRole=None, managesOrganization=None):
        super().__init__(subject)
        self.userID = userID
        self.userName = userName
        self.userEmail = userEmail
        self.userRole = userRole
        self.managesOrganization = managesOrganization


class Project(BIGGObjects):
    __rdf_type__ = Bigg.Project

    def __init__(self, subject, projectID=None, projectTitle=None, projectDescription=None, geometrySRID=None,
                 affectsBuilding=None, hasRetrofitProject=None, hasRenovationProject=None):
        super().__init__(subject)
        self.projectID = projectID
        self.projectTitle = projectTitle
        self.projectDescription = projectDescription
        self.geometrySRID = geometrySRID
        self.affectsBuilding = affectsBuilding
        self.hasRetrofitProject = hasRetrofitProject
        self.hasRenovationProject = hasRenovationProject


class RetrofitProject(BIGGObjects):
    __rdf_type__ = Bigg.RetrofitProject

    def __init__(self, subject, projectStartDate=None, projectOperationalDate=None, projectInvestment=None,
                 projectCurrencyExchangeRate=None, projectUsesIncentives=None, projectInventivesShareOfRevenues=None,
                 projectReceivedGrantFunding=None, projectGrantsShareOfCosts=None, projectDiscountRate=None,
                 projectInterestRate=None, projectInternalRateOfReturn=None, projectSimplePaybackTime=None,
                 projectNetPresentValue=None, projectSavingsToInvestmentRatio=None,
                 projectIncludedNonEnergyBenefitsEstimate=None, projectIncludedConfortmeterSurvey=None,
                 projectCO2Reduction=None, hasProjectMotivation=None, hasProjectInvestmentCurrency=None,
                 includesMeasure=None, producesSaving=None, producesNonEnergyBenefit=None):
        super().__init__(subject)
        self.projectStartDate = projectStartDate
        self.projectOperationalDate = projectOperationalDate
        self.projectInvestment = projectInvestment
        self.projectCurrencyExchangeRate = projectCurrencyExchangeRate
        self.projectUsesIncentives = projectUsesIncentives
        self.projectInventivesShareOfRevenues = projectInventivesShareOfRevenues
        self.projectReceivedGrantFunding = projectReceivedGrantFunding
        self.projectGrantsShareOfCosts = projectGrantsShareOfCosts
        self.projectDiscountRate = projectDiscountRate
        self.projectInterestRate = projectInterestRate
        self.projectInternalRateOfReturn = projectInternalRateOfReturn
        self.projectSimplePaybackTime = projectSimplePaybackTime
        self.projectNetPresentValue = projectNetPresentValue
        self.projectSavingsToInvestmentRatio = projectSavingsToInvestmentRatio
        self.projectIncludedNonEnergyBenefitsEstimate = projectIncludedNonEnergyBenefitsEstimate
        self.projectIncludedConfortmeterSurvey = projectIncludedConfortmeterSurvey
        self.projectCO2Reduction = projectCO2Reduction
        self.hasProjectMotivation = hasProjectMotivation
        self.hasProjectInvestmentCurrency = hasProjectInvestmentCurrency
        self.includesMeasure = includesMeasure
        self.producesSaving = producesSaving
        self.producesNonEnergyBenefit = producesNonEnergyBenefit


class ProjectMotivation(BIGGObjects):
    __rdf_type__ = Bigg.ProjectMotivation

    def __init__(self, subject, ):
        super().__init__(subject)


class ProjectInvestmentCurrency(BIGGObjects):
    __rdf_type__ = Bigg.ProjectInvestmentCurrency

    def __init__(self, subject, ):
        super().__init__(subject)


class RenovationProject(BIGGObjects):
    __rdf_type__ = Bigg.RenovationProject

    def __init__(self, subject, projectStartDate=None, projectOperationalDate=None, projectInvestment=None,
                 projectCurrencyExchangeRate=None, projectUsesIncentives=None, projectInventivesShareOfRevenues=None,
                 projectReceivedGrantFunding=None, projectGrantsShareOfCosts=None, projectDiscountRate=None,
                 projectInterestRate=None, projectInternalRateOfReturn=None, projectSimplePaybackTime=None,
                 projectNetPresentValue=None, projectSavingsToInvestmentRatio=None,
                 projectIncludedNonEnergyBenefitsEstimate=None, projectIncludedConfortmeterSurvey=None,
                 hasProjectMotivation=None, hasProjectInvestmentCurrency=None, producesSaving=None,
                 producesNonEnergyBenefit=None):
        super().__init__(subject)
        self.projectStartDate = projectStartDate
        self.projectOperationalDate = projectOperationalDate
        self.projectInvestment = projectInvestment
        self.projectCurrencyExchangeRate = projectCurrencyExchangeRate
        self.projectUsesIncentives = projectUsesIncentives
        self.projectInventivesShareOfRevenues = projectInventivesShareOfRevenues
        self.projectReceivedGrantFunding = projectReceivedGrantFunding
        self.projectGrantsShareOfCosts = projectGrantsShareOfCosts
        self.projectDiscountRate = projectDiscountRate
        self.projectInterestRate = projectInterestRate
        self.projectInternalRateOfReturn = projectInternalRateOfReturn
        self.projectSimplePaybackTime = projectSimplePaybackTime
        self.projectNetPresentValue = projectNetPresentValue
        self.projectSavingsToInvestmentRatio = projectSavingsToInvestmentRatio
        self.projectIncludedNonEnergyBenefitsEstimate = projectIncludedNonEnergyBenefitsEstimate
        self.projectIncludedConfortmeterSurvey = projectIncludedConfortmeterSurvey
        self.hasProjectMotivation = hasProjectMotivation
        self.hasProjectInvestmentCurrency = hasProjectInvestmentCurrency
        self.producesSaving = producesSaving
        self.producesNonEnergyBenefit = producesNonEnergyBenefit


class State(BIGGObjects):
    __rdf_type__ = Bigg.State

    def __init__(self, subject, state=None, stateStart=None, stateEnd=None, hasStateType=None):
        super().__init__(subject)
        self.state = state
        self.stateStart = stateStart
        self.stateEnd = stateEnd
        self.hasStateType = hasStateType


class StateType(BIGGObjects):
    __rdf_type__ = Bigg.StateType

    def __init__(self, subject, ):
        super().__init__(subject)


class System(BIGGObjects):
    __rdf_type__ = Bigg.System

    def __init__(self, subject, hasSystemType=None, containsElement=None, servesZone=None):
        super().__init__(subject)
        self.hasSystemType = hasSystemType
        self.containsElement = containsElement
        self.servesZone = servesZone


class SystemType(BIGGObjects):
    __rdf_type__ = Bigg.SystemType

    def __init__(self, subject, ):
        super().__init__(subject)


class Tariff(BIGGObjects):
    __rdf_type__ = Bigg.Tariff

    def __init__(self, subject, tariffCompany=None, tariffName=None, tariffEndDate=None, tariffAveragePrice=None):
        super().__init__(subject)
        self.tariffCompany = tariffCompany
        self.tariffName = tariffName
        self.tariffEndDate = tariffEndDate
        self.tariffAveragePrice = tariffAveragePrice


class UtilityPointOfDelivery(BIGGObjects):
    __rdf_type__ = Bigg.UtilityPointOfDelivery

    def __init__(self, subject, pointOfDeliveryIDFromOrganization=None, hasUtilityType=None, hasTariff=None,
                 hasCO2EmissionsFactor=None):
        super().__init__(subject)
        self.pointOfDeliveryIDFromOrganization = pointOfDeliveryIDFromOrganization
        self.hasUtilityType = hasUtilityType
        self.hasTariff = hasTariff
        self.hasCO2EmissionsFactor = hasCO2EmissionsFactor


class UtilityType(BIGGObjects):
    __rdf_type__ = Bigg.UtilityType

    def __init__(self, subject, ):
        super().__init__(subject)


class WeatherStation(BIGGObjects):
    __rdf_type__ = Bigg.WeatherStation

    def __init__(self, subject, weatherStationCoordinates=None, hasWeatherStationType=None, hasDevice=None):
        super().__init__(subject)
        self.weatherStationCoordinates = weatherStationCoordinates
        self.hasWeatherStationType = hasWeatherStationType
        self.hasDevice = hasDevice


class WeatherStationType(BIGGObjects):
    __rdf_type__ = Bigg.WeatherStationType

    def __init__(self, subject, ):
        super().__init__(subject)


class Zone(BIGGObjects):
    __rdf_type__ = Bigg.Zone

    def __init__(self, subject, hasZoneType=None, isContainedInZone=None):
        super().__init__(subject)
        self.hasZoneType = hasZoneType
        self.isContainedInZone = isContainedInZone


class ZoneType(BIGGObjects):
    __rdf_type__ = Bigg.ZoneType

    def __init__(self, subject, ):
        super().__init__(subject)
