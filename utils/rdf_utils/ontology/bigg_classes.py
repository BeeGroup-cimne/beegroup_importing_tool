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
    
        
class AddressCity(BIGGObjects):
    __rdf_type__ = Bigg.AddressCity

    def __init__(self, subject, name=None,comment=None,label=None):
        super().__init__(subject)
        self.name = name
        self.comment = comment
        self.label = label
        
        
class AddressCountry(BIGGObjects):
    __rdf_type__ = Bigg.AddressCountry

    def __init__(self, subject, name=None,comment=None,label=None):
        super().__init__(subject)
        self.name = name
        self.comment = comment
        self.label = label
        
        
class AddressProvince(BIGGObjects):
    __rdf_type__ = Bigg.AddressProvince

    def __init__(self, subject, name=None,comment=None,label=None):
        super().__init__(subject)
        self.name = name
        self.comment = comment
        self.label = label
        
        
class EnergyPerformanceContract(BIGGObjects):
    __rdf_type__ = Bigg.EnergyPerformanceContract

    def __init__(self, subject, contractEndDate=None,contractName=None,contractPerimeter=None,contractStartDate=None,comment=None,label=None,hasObjective=None,providesContract=None):
        super().__init__(subject)
        self.contractEndDate = contractEndDate
        self.contractName = contractName
        self.contractPerimeter = contractPerimeter
        self.contractStartDate = contractStartDate
        self.comment = comment
        self.label = label
        self.hasObjective = hasObjective
        self.providesContract = providesContract
        
        
class Element(BIGGObjects):
    __rdf_type__ = Bigg.Element

    def __init__(self, subject, comment=None,label=None,isObservedByDevice=None,hasSubElement=None,isAffectedByMeasure=None,isAssociatedWithSpace=None,isContainedInSpace=None,maintainsElement=None,containsSystem=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.isObservedByDevice = isObservedByDevice
        self.hasSubElement = hasSubElement
        self.isAffectedByMeasure = isAffectedByMeasure
        self.isAssociatedWithSpace = isAssociatedWithSpace
        self.isContainedInSpace = isContainedInSpace
        self.maintainsElement = maintainsElement
        self.containsSystem = containsSystem
        
        
class Measurement(BIGGObjects):
    __rdf_type__ = Bigg.Measurement

    def __init__(self, subject, comment=None,label=None,end=None,isReal=None,start=None,value=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.end = end
        self.isReal = isReal
        self.start = start
        self.value = value
        
        
class StatePoint(BIGGObjects):
    __rdf_type__ = Bigg.StatePoint

    def __init__(self, subject, comment=None,label=None,end=None,isReal=None,start=None,value=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.end = end
        self.isReal = isReal
        self.start = start
        self.value = value
        
        
class WeatherStation(BIGGObjects):
    __rdf_type__ = Bigg.WeatherStation

    def __init__(self, subject, comment=None,label=None,deviceIDFromOrganization=None,deviceInstallationDate=None,deviceLicenceVersionNumber=None,deviceManufacturer=None,deviceModel=None,deviceName=None,deviceNumberOfOutputs=None,deviceOperatingSystem=None,deviceRemovalDate=None,deviceSerialNumber=None,deviceThresholdValue=None,latitude=None,longitude=None,hasDeviceInputProtocol=None,hasDeviceInputSignalType=None,hasDeviceType=None,hasHistory=None,hasSensor=None,hasState=None,hasUtilityPointofDelivery=None,isPartOfDeviceAggregator=None,observes=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.deviceIDFromOrganization = deviceIDFromOrganization
        self.deviceInstallationDate = deviceInstallationDate
        self.deviceLicenceVersionNumber = deviceLicenceVersionNumber
        self.deviceManufacturer = deviceManufacturer
        self.deviceModel = deviceModel
        self.deviceName = deviceName
        self.deviceNumberOfOutputs = deviceNumberOfOutputs
        self.deviceOperatingSystem = deviceOperatingSystem
        self.deviceRemovalDate = deviceRemovalDate
        self.deviceSerialNumber = deviceSerialNumber
        self.deviceThresholdValue = deviceThresholdValue
        self.latitude = latitude
        self.longitude = longitude
        self.hasDeviceInputProtocol = hasDeviceInputProtocol
        self.hasDeviceInputSignalType = hasDeviceInputSignalType
        self.hasDeviceType = hasDeviceType
        self.hasHistory = hasHistory
        self.hasSensor = hasSensor
        self.hasState = hasState
        self.hasUtilityPointofDelivery = hasUtilityPointofDelivery
        self.isPartOfDeviceAggregator = isPartOfDeviceAggregator
        self.observes = observes
        
        
class State(BIGGObjects):
    __rdf_type__ = Bigg.State

    def __init__(self, subject, comment=None,label=None,TimeSeriesEnd=None,TimeSeriesFrequency=None,TimeSeriesIsCumulative=None,TimeSeriesIsOnChange=None,TimeSeriesIsRegular=None,TimeSeriesStart=None,TimeSeriesTimeAggregationFunction=None,hasMeasuredProperty=None,hasStatePoint=None,hasStateType=None,hasStateUnit=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.TimeSeriesEnd = TimeSeriesEnd
        self.TimeSeriesFrequency = TimeSeriesFrequency
        self.TimeSeriesIsCumulative = TimeSeriesIsCumulative
        self.TimeSeriesIsOnChange = TimeSeriesIsOnChange
        self.TimeSeriesIsRegular = TimeSeriesIsRegular
        self.TimeSeriesStart = TimeSeriesStart
        self.TimeSeriesTimeAggregationFunction = TimeSeriesTimeAggregationFunction
        self.hasMeasuredProperty = hasMeasuredProperty
        self.hasStatePoint = hasStatePoint
        self.hasStateType = hasStateType
        self.hasStateUnit = hasStateUnit
        
        
class BuildingSpace(BIGGObjects):
    __rdf_type__ = Bigg.BuildingSpace

    def __init__(self, subject, comment=None,label=None,buildingSpaceIDFromOrganization=None,buildingSpaceName=None,hasDeviceAggregator=None,hasSubSpace=None,isObservedByDevice=None,containsElement=None,hasArea=None,hasBuildingSpaceUseType=None,hasIndoorQualityPerception=None,hasOccupancyProfile=None,isAssociatedWithElement=None,containsZone=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.buildingSpaceIDFromOrganization = buildingSpaceIDFromOrganization
        self.buildingSpaceName = buildingSpaceName
        self.hasDeviceAggregator = hasDeviceAggregator
        self.hasSubSpace = hasSubSpace
        self.isObservedByDevice = isObservedByDevice
        self.containsElement = containsElement
        self.hasArea = hasArea
        self.hasBuildingSpaceUseType = hasBuildingSpaceUseType
        self.hasIndoorQualityPerception = hasIndoorQualityPerception
        self.hasOccupancyProfile = hasOccupancyProfile
        self.isAssociatedWithElement = isAssociatedWithElement
        self.containsZone = containsZone
        
        
class Sensor(BIGGObjects):
    __rdf_type__ = Bigg.Sensor

    def __init__(self, subject, comment=None,label=None,TimeSeriesEnd=None,TimeSeriesFrequency=None,TimeSeriesIsCumulative=None,TimeSeriesIsOnChange=None,TimeSeriesIsRegular=None,TimeSeriesStart=None,TimeSeriesTimeAggregationFunction=None,hasMeasuredProperty=None,hasMeasurement=None,hasMeasurementUnit=None,hasOutputProtocol=None,hasOutputSignalType=None,hasSensorEstimationMethod=None,hasSensorReadingType=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.TimeSeriesEnd = TimeSeriesEnd
        self.TimeSeriesFrequency = TimeSeriesFrequency
        self.TimeSeriesIsCumulative = TimeSeriesIsCumulative
        self.TimeSeriesIsOnChange = TimeSeriesIsOnChange
        self.TimeSeriesIsRegular = TimeSeriesIsRegular
        self.TimeSeriesStart = TimeSeriesStart
        self.TimeSeriesTimeAggregationFunction = TimeSeriesTimeAggregationFunction
        self.hasMeasuredProperty = hasMeasuredProperty
        self.hasMeasurement = hasMeasurement
        self.hasMeasurementUnit = hasMeasurementUnit
        self.hasOutputProtocol = hasOutputProtocol
        self.hasOutputSignalType = hasOutputSignalType
        self.hasSensorEstimationMethod = hasSensorEstimationMethod
        self.hasSensorReadingType = hasSensorReadingType
        
        
class Device(BIGGObjects):
    __rdf_type__ = Bigg.Device

    def __init__(self, subject, comment=None,label=None,deviceIDFromOrganization=None,deviceInstallationDate=None,deviceLicenceVersionNumber=None,deviceManufacturer=None,deviceModel=None,deviceName=None,deviceNumberOfOutputs=None,deviceOperatingSystem=None,deviceRemovalDate=None,deviceSerialNumber=None,deviceThresholdValue=None,hasDeviceInputProtocol=None,hasDeviceInputSignalType=None,hasDeviceType=None,hasHistory=None,hasSensor=None,hasState=None,hasUtilityPointofDelivery=None,isPartOfDeviceAggregator=None,observes=None,hasSubElement=None,isAffectedByMeasure=None,isAssociatedWithSpace=None,isContainedInSpace=None,maintainsElement=None,containsSystem=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.deviceIDFromOrganization = deviceIDFromOrganization
        self.deviceInstallationDate = deviceInstallationDate
        self.deviceLicenceVersionNumber = deviceLicenceVersionNumber
        self.deviceManufacturer = deviceManufacturer
        self.deviceModel = deviceModel
        self.deviceName = deviceName
        self.deviceNumberOfOutputs = deviceNumberOfOutputs
        self.deviceOperatingSystem = deviceOperatingSystem
        self.deviceRemovalDate = deviceRemovalDate
        self.deviceSerialNumber = deviceSerialNumber
        self.deviceThresholdValue = deviceThresholdValue
        self.hasDeviceInputProtocol = hasDeviceInputProtocol
        self.hasDeviceInputSignalType = hasDeviceInputSignalType
        self.hasDeviceType = hasDeviceType
        self.hasHistory = hasHistory
        self.hasSensor = hasSensor
        self.hasState = hasState
        self.hasUtilityPointofDelivery = hasUtilityPointofDelivery
        self.isPartOfDeviceAggregator = isPartOfDeviceAggregator
        self.observes = observes
        self.hasSubElement = hasSubElement
        self.isAffectedByMeasure = isAffectedByMeasure
        self.isAssociatedWithSpace = isAssociatedWithSpace
        self.isContainedInSpace = isContainedInSpace
        self.maintainsElement = maintainsElement
        self.containsSystem = containsSystem
        
        
class BuildingConstructionElement(BIGGObjects):
    __rdf_type__ = Bigg.BuildingConstructionElement

    def __init__(self, subject, comment=None,label=None,buildingElementBrand=None,buildingElementIdFromOrganizationstring=None,buildingElementInstallationDate=None,buildingElementManufactureDatestring=None,buildingElementManufacturer=None,buildingElementModelstring=None,buildingElementPurchaseDate=None,buildingElementSerialNumber=None,buildingElementState=None,hasBuildingConstructionElementType=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.buildingElementBrand = buildingElementBrand
        self.buildingElementIdFromOrganizationstring = buildingElementIdFromOrganizationstring
        self.buildingElementInstallationDate = buildingElementInstallationDate
        self.buildingElementManufactureDatestring = buildingElementManufactureDatestring
        self.buildingElementManufacturer = buildingElementManufacturer
        self.buildingElementModelstring = buildingElementModelstring
        self.buildingElementPurchaseDate = buildingElementPurchaseDate
        self.buildingElementSerialNumber = buildingElementSerialNumber
        self.buildingElementState = buildingElementState
        self.hasBuildingConstructionElementType = hasBuildingConstructionElementType
        
        
class BuildingSystemElement(BIGGObjects):
    __rdf_type__ = Bigg.BuildingSystemElement

    def __init__(self, subject, comment=None,label=None,buildingElementBrand=None,buildingElementIdFromOrganizationstring=None,buildingElementInstallationDate=None,buildingElementManufactureDatestring=None,buildingElementManufacturer=None,buildingElementModelstring=None,buildingElementPurchaseDate=None,buildingElementSerialNumber=None,buildingElementState=None,buildingSystemElementEfficiency=None,buildingSystemElementMaxOutput=None,buildingSystemElementMinOutput=None,hasBuildingSystemElementType=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.buildingElementBrand = buildingElementBrand
        self.buildingElementIdFromOrganizationstring = buildingElementIdFromOrganizationstring
        self.buildingElementInstallationDate = buildingElementInstallationDate
        self.buildingElementManufactureDatestring = buildingElementManufactureDatestring
        self.buildingElementManufacturer = buildingElementManufacturer
        self.buildingElementModelstring = buildingElementModelstring
        self.buildingElementPurchaseDate = buildingElementPurchaseDate
        self.buildingElementSerialNumber = buildingElementSerialNumber
        self.buildingElementState = buildingElementState
        self.buildingSystemElementEfficiency = buildingSystemElementEfficiency
        self.buildingSystemElementMaxOutput = buildingSystemElementMaxOutput
        self.buildingSystemElementMinOutput = buildingSystemElementMinOutput
        self.hasBuildingSystemElementType = hasBuildingSystemElementType
        
        
class BuildingElement(BIGGObjects):
    __rdf_type__ = Bigg.BuildingElement

    def __init__(self, subject, comment=None,label=None,buildingElementBrand=None,buildingElementIdFromOrganizationstring=None,buildingElementInstallationDate=None,buildingElementManufactureDatestring=None,buildingElementManufacturer=None,buildingElementModelstring=None,buildingElementPurchaseDate=None,buildingElementSerialNumber=None,buildingElementState=None,hasSubElement=None,isAffectedByMeasure=None,isAssociatedWithSpace=None,isContainedInSpace=None,maintainsElement=None,containsSystem=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.buildingElementBrand = buildingElementBrand
        self.buildingElementIdFromOrganizationstring = buildingElementIdFromOrganizationstring
        self.buildingElementInstallationDate = buildingElementInstallationDate
        self.buildingElementManufactureDatestring = buildingElementManufactureDatestring
        self.buildingElementManufacturer = buildingElementManufacturer
        self.buildingElementModelstring = buildingElementModelstring
        self.buildingElementPurchaseDate = buildingElementPurchaseDate
        self.buildingElementSerialNumber = buildingElementSerialNumber
        self.buildingElementState = buildingElementState
        self.hasSubElement = hasSubElement
        self.isAffectedByMeasure = isAffectedByMeasure
        self.isAssociatedWithSpace = isAssociatedWithSpace
        self.isContainedInSpace = isContainedInSpace
        self.maintainsElement = maintainsElement
        self.containsSystem = containsSystem
        
        
class EnergyEfficiencyMeasure(BIGGObjects):
    __rdf_type__ = Bigg.EnergyEfficiencyMeasure

    def __init__(self, subject, comment=None,label=None,EneergyEfficiencyMeasureCurrencyExhangeRate=None,EneergyEfficiencyMeasureFinancialSavings=None,EneergyEfficiencyMeasureOperationalDate=None,EneergyEfficiencyMeasureSavingsToInvestmenRatio=None,energyEfficiencyMeasureCO2Reduction=None,energyEfficiencyMeasureDescription=None,energyEfficiencyMeasureInvestment=None,energyEfficiencyMeasureLifetime=None,energySourcePriceEscalationRate=None,shareOfAffectedElement=None,affectsElement=None,hasEnergyEfficiencyMeasureInvestmentCurrency=None,hasEnergyEfficiencyMeasureType=None,producesNonEnergyBenefit=None,producesSaving=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.EneergyEfficiencyMeasureCurrencyExhangeRate = EneergyEfficiencyMeasureCurrencyExhangeRate
        self.EneergyEfficiencyMeasureFinancialSavings = EneergyEfficiencyMeasureFinancialSavings
        self.EneergyEfficiencyMeasureOperationalDate = EneergyEfficiencyMeasureOperationalDate
        self.EneergyEfficiencyMeasureSavingsToInvestmenRatio = EneergyEfficiencyMeasureSavingsToInvestmenRatio
        self.energyEfficiencyMeasureCO2Reduction = energyEfficiencyMeasureCO2Reduction
        self.energyEfficiencyMeasureDescription = energyEfficiencyMeasureDescription
        self.energyEfficiencyMeasureInvestment = energyEfficiencyMeasureInvestment
        self.energyEfficiencyMeasureLifetime = energyEfficiencyMeasureLifetime
        self.energySourcePriceEscalationRate = energySourcePriceEscalationRate
        self.shareOfAffectedElement = shareOfAffectedElement
        self.affectsElement = affectsElement
        self.hasEnergyEfficiencyMeasureInvestmentCurrency = hasEnergyEfficiencyMeasureInvestmentCurrency
        self.hasEnergyEfficiencyMeasureType = hasEnergyEfficiencyMeasureType
        self.producesNonEnergyBenefit = producesNonEnergyBenefit
        self.producesSaving = producesSaving
        
        
class System(BIGGObjects):
    __rdf_type__ = Bigg.System

    def __init__(self, subject, comment=None,label=None,groupName=None,hasSystemType=None,isContainedInSystem=None,servesZone=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.groupName = groupName
        self.hasSystemType = hasSystemType
        self.isContainedInSystem = isContainedInSystem
        self.servesZone = servesZone
        
        
class Zone(BIGGObjects):
    __rdf_type__ = Bigg.Zone

    def __init__(self, subject, comment=None,label=None,groupName=None,hasZoneType=None,isContainedInZone=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.groupName = groupName
        self.hasZoneType = hasZoneType
        self.isContainedInZone = isContainedInZone
        
        
class RenovationProject(BIGGObjects):
    __rdf_type__ = Bigg.RenovationProject

    def __init__(self, subject, comment=None,label=None,geometrySRID=None,projectCurrencyExchangeRate=None,projectDescription=None,projectDiscountRate=None,projectGrantsShareOfCosts=None,projectIDFromOrganization=None,projectIncludedConfortmeterSurvey=None,projectIncludedNonEnergyBenefitsEstimate=None,projectInterestRate=None,projectInternalRateOfReturn=None,projectInventivesShareOfRevenues=None,projectInvestment=None,projectName=None,projectNetPresentValue=None,projectOperationalDate=None,projectReceivedGrantFounding=None,projectSavingsToInvestmentRatio=None,projectSimplePaybackTime=None,projectStartDate=None,projectUsesIncentives=None,affectsBuilding=None,hasProjectInvestmentCurrency=None,hasProjectMotivation=None,hasSubProject=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.geometrySRID = geometrySRID
        self.projectCurrencyExchangeRate = projectCurrencyExchangeRate
        self.projectDescription = projectDescription
        self.projectDiscountRate = projectDiscountRate
        self.projectGrantsShareOfCosts = projectGrantsShareOfCosts
        self.projectIDFromOrganization = projectIDFromOrganization
        self.projectIncludedConfortmeterSurvey = projectIncludedConfortmeterSurvey
        self.projectIncludedNonEnergyBenefitsEstimate = projectIncludedNonEnergyBenefitsEstimate
        self.projectInterestRate = projectInterestRate
        self.projectInternalRateOfReturn = projectInternalRateOfReturn
        self.projectInventivesShareOfRevenues = projectInventivesShareOfRevenues
        self.projectInvestment = projectInvestment
        self.projectName = projectName
        self.projectNetPresentValue = projectNetPresentValue
        self.projectOperationalDate = projectOperationalDate
        self.projectReceivedGrantFounding = projectReceivedGrantFounding
        self.projectSavingsToInvestmentRatio = projectSavingsToInvestmentRatio
        self.projectSimplePaybackTime = projectSimplePaybackTime
        self.projectStartDate = projectStartDate
        self.projectUsesIncentives = projectUsesIncentives
        self.affectsBuilding = affectsBuilding
        self.hasProjectInvestmentCurrency = hasProjectInvestmentCurrency
        self.hasProjectMotivation = hasProjectMotivation
        self.hasSubProject = hasSubProject
        
        
class RetrofitProject(BIGGObjects):
    __rdf_type__ = Bigg.RetrofitProject

    def __init__(self, subject, comment=None,label=None,geometrySRID=None,projectCO2Reduction=None,projectCurrencyExchangeRate=None,projectDescription=None,projectDiscountRate=None,projectGrantsShareOfCosts=None,projectIDFromOrganization=None,projectIncludedConfortmeterSurvey=None,projectIncludedNonEnergyBenefitsEstimate=None,projectInterestRate=None,projectInternalRateOfReturn=None,projectInventivesShareOfRevenues=None,projectInvestment=None,projectName=None,projectNetPresentValue=None,projectOperationalDate=None,projectReceivedGrantFounding=None,projectSavingsToInvestmentRatio=None,projectSimplePaybackTime=None,projectStartDate=None,projectUsesIncentives=None,affectsBuilding=None,hasProjectInvestmentCurrency=None,hasProjectMotivation=None,hasSubProject=None,includesMeasure=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.geometrySRID = geometrySRID
        self.projectCO2Reduction = projectCO2Reduction
        self.projectCurrencyExchangeRate = projectCurrencyExchangeRate
        self.projectDescription = projectDescription
        self.projectDiscountRate = projectDiscountRate
        self.projectGrantsShareOfCosts = projectGrantsShareOfCosts
        self.projectIDFromOrganization = projectIDFromOrganization
        self.projectIncludedConfortmeterSurvey = projectIncludedConfortmeterSurvey
        self.projectIncludedNonEnergyBenefitsEstimate = projectIncludedNonEnergyBenefitsEstimate
        self.projectInterestRate = projectInterestRate
        self.projectInternalRateOfReturn = projectInternalRateOfReturn
        self.projectInventivesShareOfRevenues = projectInventivesShareOfRevenues
        self.projectInvestment = projectInvestment
        self.projectName = projectName
        self.projectNetPresentValue = projectNetPresentValue
        self.projectOperationalDate = projectOperationalDate
        self.projectReceivedGrantFounding = projectReceivedGrantFounding
        self.projectSavingsToInvestmentRatio = projectSavingsToInvestmentRatio
        self.projectSimplePaybackTime = projectSimplePaybackTime
        self.projectStartDate = projectStartDate
        self.projectUsesIncentives = projectUsesIncentives
        self.affectsBuilding = affectsBuilding
        self.hasProjectInvestmentCurrency = hasProjectInvestmentCurrency
        self.hasProjectMotivation = hasProjectMotivation
        self.hasSubProject = hasSubProject
        self.includesMeasure = includesMeasure
        
        
class Project(BIGGObjects):
    __rdf_type__ = Bigg.Project

    def __init__(self, subject, comment=None,label=None,geometrySRID=None,projectCurrencyExchangeRate=None,projectDescription=None,projectDiscountRate=None,projectGrantsShareOfCosts=None,projectIDFromOrganization=None,projectIncludedConfortmeterSurvey=None,projectIncludedNonEnergyBenefitsEstimate=None,projectInterestRate=None,projectInternalRateOfReturn=None,projectInventivesShareOfRevenues=None,projectInvestment=None,projectName=None,projectNetPresentValue=None,projectOperationalDate=None,projectReceivedGrantFounding=None,projectSavingsToInvestmentRatio=None,projectSimplePaybackTime=None,projectStartDate=None,projectUsesIncentives=None,affectsBuilding=None,hasProjectInvestmentCurrency=None,hasProjectMotivation=None,hasSubProject=None,producesNonEnergyBenefit=None,producesSaving=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.geometrySRID = geometrySRID
        self.projectCurrencyExchangeRate = projectCurrencyExchangeRate
        self.projectDescription = projectDescription
        self.projectDiscountRate = projectDiscountRate
        self.projectGrantsShareOfCosts = projectGrantsShareOfCosts
        self.projectIDFromOrganization = projectIDFromOrganization
        self.projectIncludedConfortmeterSurvey = projectIncludedConfortmeterSurvey
        self.projectIncludedNonEnergyBenefitsEstimate = projectIncludedNonEnergyBenefitsEstimate
        self.projectInterestRate = projectInterestRate
        self.projectInternalRateOfReturn = projectInternalRateOfReturn
        self.projectInventivesShareOfRevenues = projectInventivesShareOfRevenues
        self.projectInvestment = projectInvestment
        self.projectName = projectName
        self.projectNetPresentValue = projectNetPresentValue
        self.projectOperationalDate = projectOperationalDate
        self.projectReceivedGrantFounding = projectReceivedGrantFounding
        self.projectSavingsToInvestmentRatio = projectSavingsToInvestmentRatio
        self.projectSimplePaybackTime = projectSimplePaybackTime
        self.projectStartDate = projectStartDate
        self.projectUsesIncentives = projectUsesIncentives
        self.affectsBuilding = affectsBuilding
        self.hasProjectInvestmentCurrency = hasProjectInvestmentCurrency
        self.hasProjectMotivation = hasProjectMotivation
        self.hasSubProject = hasSubProject
        self.producesNonEnergyBenefit = producesNonEnergyBenefit
        self.producesSaving = producesSaving
        
        
class CO2EmissionsPoint(BIGGObjects):
    __rdf_type__ = Bigg.CO2EmissionsPoint

    def __init__(self, subject, comment=None,label=None,end=None,isReal=None,start=None,value=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.end = end
        self.isReal = isReal
        self.start = start
        self.value = value
        
        
class TariffPoint(BIGGObjects):
    __rdf_type__ = Bigg.TariffPoint

    def __init__(self, subject, comment=None,label=None,end=None,isReal=None,start=None,value=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.end = end
        self.isReal = isReal
        self.start = start
        self.value = value
        
        
class CO2EmissionsFactor(BIGGObjects):
    __rdf_type__ = Bigg.CO2EmissionsFactor

    def __init__(self, subject, comment=None,label=None,TimeSeriesEnd=None,TimeSeriesFrequency=None,TimeSeriesIsCumulative=None,TimeSeriesIsOnChange=None,TimeSeriesIsRegular=None,TimeSeriesStart=None,TimeSeriesTimeAggregationFunction=None,hasMeasuredProperty=None,hasCO2EmsissionsPoint=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.TimeSeriesEnd = TimeSeriesEnd
        self.TimeSeriesFrequency = TimeSeriesFrequency
        self.TimeSeriesIsCumulative = TimeSeriesIsCumulative
        self.TimeSeriesIsOnChange = TimeSeriesIsOnChange
        self.TimeSeriesIsRegular = TimeSeriesIsRegular
        self.TimeSeriesStart = TimeSeriesStart
        self.TimeSeriesTimeAggregationFunction = TimeSeriesTimeAggregationFunction
        self.hasMeasuredProperty = hasMeasuredProperty
        self.hasCO2EmsissionsPoint = hasCO2EmsissionsPoint
        
        
class Tariff(BIGGObjects):
    __rdf_type__ = Bigg.Tariff

    def __init__(self, subject, contractEndDate=None,contractName=None,contractStartDate=None,comment=None,label=None,TimeSeriesEnd=None,TimeSeriesFrequency=None,TimeSeriesIsCumulative=None,TimeSeriesIsOnChange=None,TimeSeriesIsRegular=None,TimeSeriesStart=None,TimeSeriesTimeAggregationFunction=None,tariffCompany=None,tariffName=None,hasMeasuredProperty=None,hasTariffPoint=None,tariffCurrencyUnit=None):
        super().__init__(subject)
        self.contractEndDate = contractEndDate
        self.contractName = contractName
        self.contractStartDate = contractStartDate
        self.comment = comment
        self.label = label
        self.TimeSeriesEnd = TimeSeriesEnd
        self.TimeSeriesFrequency = TimeSeriesFrequency
        self.TimeSeriesIsCumulative = TimeSeriesIsCumulative
        self.TimeSeriesIsOnChange = TimeSeriesIsOnChange
        self.TimeSeriesIsRegular = TimeSeriesIsRegular
        self.TimeSeriesStart = TimeSeriesStart
        self.TimeSeriesTimeAggregationFunction = TimeSeriesTimeAggregationFunction
        self.tariffCompany = tariffCompany
        self.tariffName = tariffName
        self.hasMeasuredProperty = hasMeasuredProperty
        self.hasTariffPoint = hasTariffPoint
        self.tariffCurrencyUnit = tariffCurrencyUnit
        
        
class AddressClimateZone(BIGGObjects):
    __rdf_type__ = Bigg.AddressClimateZone

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class BuildingConstructionType(BIGGObjects):
    __rdf_type__ = Bigg.BuildingConstructionType

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class BuildingOwnership(BIGGObjects):
    __rdf_type__ = Bigg.BuildingOwnership

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class LandType(BIGGObjects):
    __rdf_type__ = Bigg.LandType

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class ObjectiveTargetType(BIGGObjects):
    __rdf_type__ = Bigg.ObjectiveTargetType

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class ObjectiveTargetUnit(BIGGObjects):
    __rdf_type__ = Bigg.ObjectiveTargetUnit

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class OrganiationType(BIGGObjects):
    __rdf_type__ = Bigg.OrganiationType

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class Contract(BIGGObjects):
    __rdf_type__ = Bigg.Contract

    def __init__(self, subject, contractEndDate=None,contractName=None,contractStartDate=None,comment=None,label=None):
        super().__init__(subject)
        self.contractEndDate = contractEndDate
        self.contractName = contractName
        self.contractStartDate = contractStartDate
        self.comment = comment
        self.label = label
        
        
class Feature(BIGGObjects):
    __rdf_type__ = Bigg.Feature

    def __init__(self, subject, name=None,comment=None,label=None):
        super().__init__(subject)
        self.name = name
        self.comment = comment
        self.label = label
        
        
class CadastralInfo(BIGGObjects):
    __rdf_type__ = Bigg.CadastralInfo

    def __init__(self, subject, landArea=None,landCadastralReference=None,landGeometry=None,landGraphicalArea=None,propertyClass=None,comment=None,label=None,hasLandType=None):
        super().__init__(subject)
        self.landArea = landArea
        self.landCadastralReference = landCadastralReference
        self.landGeometry = landGeometry
        self.landGraphicalArea = landGraphicalArea
        self.propertyClass = propertyClass
        self.comment = comment
        self.label = label
        self.hasLandType = hasLandType
        
        
class EnergyPerformanceContractObjective(BIGGObjects):
    __rdf_type__ = Bigg.EnergyPerformanceContractObjective

    def __init__(self, subject, objectiveDeadline=None,objectiveDescription=None,objectiveName=None,objectiveTargetValue=None,comment=None,label=None,hasObjectiveTargetType=None,hasObjectiveTargetUnit=None,IsConnectedToEnergySaving=None):
        super().__init__(subject)
        self.objectiveDeadline = objectiveDeadline
        self.objectiveDescription = objectiveDescription
        self.objectiveName = objectiveName
        self.objectiveTargetValue = objectiveTargetValue
        self.comment = comment
        self.label = label
        self.hasObjectiveTargetType = hasObjectiveTargetType
        self.hasObjectiveTargetUnit = hasObjectiveTargetUnit
        self.IsConnectedToEnergySaving = IsConnectedToEnergySaving
        
        
class Person(BIGGObjects):
    __rdf_type__ = Bigg.Person

    def __init__(self, subject, email=None,lastName=None,name=None,userName=None,comment=None,label=None,managesOrganization=None):
        super().__init__(subject)
        self.email = email
        self.lastName = lastName
        self.name = name
        self.userName = userName
        self.comment = comment
        self.label = label
        self.managesOrganization = managesOrganization
        
        
class Building(BIGGObjects):
    __rdf_type__ = Bigg.Building

    def __init__(self, subject, buildingClosingHour=None,buildingConstructionYear=None,buildingIDFromOrganization=None,buildingName=None,buildingOpeningHour=None,comment=None,label=None,hasBuildingConstructionType=None,hasBuildingOwnership=None,hasCadastralInfo=None,hasLocationInfo=None,pertainsToOrganization=None,hasSpace=None,hasEPC=None,hasProject=None):
        super().__init__(subject)
        self.buildingClosingHour = buildingClosingHour
        self.buildingConstructionYear = buildingConstructionYear
        self.buildingIDFromOrganization = buildingIDFromOrganization
        self.buildingName = buildingName
        self.buildingOpeningHour = buildingOpeningHour
        self.comment = comment
        self.label = label
        self.hasBuildingConstructionType = hasBuildingConstructionType
        self.hasBuildingOwnership = hasBuildingOwnership
        self.hasCadastralInfo = hasCadastralInfo
        self.hasLocationInfo = hasLocationInfo
        self.pertainsToOrganization = pertainsToOrganization
        self.hasSpace = hasSpace
        self.hasEPC = hasEPC
        self.hasProject = hasProject
        
        
class LocationInfo(BIGGObjects):
    __rdf_type__ = Bigg.LocationInfo

    def __init__(self, subject, addressAltitude=None,addressLatitude=None,addressLongitude=None,addressPostalCode=None,addressStreetName=None,addressStreetNumber=None,comment=None,label=None,hasAddressCity=None,hasAddressClimateZone=None,hasAddressCountry=None,hasAddressProvince=None):
        super().__init__(subject)
        self.addressAltitude = addressAltitude
        self.addressLatitude = addressLatitude
        self.addressLongitude = addressLongitude
        self.addressPostalCode = addressPostalCode
        self.addressStreetName = addressStreetName
        self.addressStreetNumber = addressStreetNumber
        self.comment = comment
        self.label = label
        self.hasAddressCity = hasAddressCity
        self.hasAddressClimateZone = hasAddressClimateZone
        self.hasAddressCountry = hasAddressCountry
        self.hasAddressProvince = hasAddressProvince
        
        
class Organization(BIGGObjects):
    __rdf_type__ = Bigg.Organization

    def __init__(self, subject, organizationDivisionType=None,organizationEmail=None,organizationLocalVAT=None,organizationName=None,organizationTelephoneNumber=None,comment=None,label=None,buysContract=None,hasOrganizationType=None,hasSubOrganization=None,isManagedByPerson=None,managesBuilding=None,organizationContactPerson=None):
        super().__init__(subject)
        self.organizationDivisionType = organizationDivisionType
        self.organizationEmail = organizationEmail
        self.organizationLocalVAT = organizationLocalVAT
        self.organizationName = organizationName
        self.organizationTelephoneNumber = organizationTelephoneNumber
        self.comment = comment
        self.label = label
        self.buysContract = buysContract
        self.hasOrganizationType = hasOrganizationType
        self.hasSubOrganization = hasSubOrganization
        self.isManagedByPerson = isManagedByPerson
        self.managesBuilding = managesBuilding
        self.organizationContactPerson = organizationContactPerson
        
        
class DeviceInputProtocol(BIGGObjects):
    __rdf_type__ = Bigg.DeviceInputProtocol

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class DeviceInputSignalType(BIGGObjects):
    __rdf_type__ = Bigg.DeviceInputSignalType

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class DeviceType(BIGGObjects):
    __rdf_type__ = Bigg.DeviceType

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class OutputProtocol(BIGGObjects):
    __rdf_type__ = Bigg.OutputProtocol

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class OutputSignalType(BIGGObjects):
    __rdf_type__ = Bigg.OutputSignalType

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class SensorEstimationMethod(BIGGObjects):
    __rdf_type__ = Bigg.SensorEstimationMethod

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class SensorReadingType(BIGGObjects):
    __rdf_type__ = Bigg.SensorReadingType

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class StateType(BIGGObjects):
    __rdf_type__ = Bigg.StateType

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class UtilityType(BIGGObjects):
    __rdf_type__ = Bigg.UtilityType

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class DeviceHistory(BIGGObjects):
    __rdf_type__ = Bigg.DeviceHistory

    def __init__(self, subject, comment=None,label=None,containsHistoryDevices=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.containsHistoryDevices = containsHistoryDevices
        
        
class MeasuredProperty(BIGGObjects):
    __rdf_type__ = Bigg.MeasuredProperty

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class MeasurementUnit(BIGGObjects):
    __rdf_type__ = Bigg.MeasurementUnit

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class UtilityPointOfDelivery(BIGGObjects):
    __rdf_type__ = Bigg.UtilityPointOfDelivery

    def __init__(self, subject, comment=None,label=None,pointOfDeliveryIDFromOrganization=None,hasUtilityType=None,hasCO2EmissionsFactor=None,hasContractedTariff=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.pointOfDeliveryIDFromOrganization = pointOfDeliveryIDFromOrganization
        self.hasUtilityType = hasUtilityType
        self.hasCO2EmissionsFactor = hasCO2EmissionsFactor
        self.hasContractedTariff = hasContractedTariff
        
        
class ObservableItem(BIGGObjects):
    __rdf_type__ = Bigg.ObservableItem

    def __init__(self, subject, comment=None,label=None,isObservedByDevice=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.isObservedByDevice = isObservedByDevice
        
        
class TimeseriesPoint(BIGGObjects):
    __rdf_type__ = Bigg.TimeseriesPoint

    def __init__(self, subject, comment=None,label=None,end=None,isReal=None,start=None,value=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.end = end
        self.isReal = isReal
        self.start = start
        self.value = value
        
        
class DeviceAggregator(BIGGObjects):
    __rdf_type__ = Bigg.DeviceAggregator

    def __init__(self, subject, comment=None,label=None,deviceAggregatorFormula=None,deviceAggregatorFrequency=None,deviceAggregatorName=None,deviceAggregatorTimeAggregationFunction=None,aggregatesSpace=None,hasDeviceAggregatorProperty=None,includesDevice=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.deviceAggregatorFormula = deviceAggregatorFormula
        self.deviceAggregatorFrequency = deviceAggregatorFrequency
        self.deviceAggregatorName = deviceAggregatorName
        self.deviceAggregatorTimeAggregationFunction = deviceAggregatorTimeAggregationFunction
        self.aggregatesSpace = aggregatesSpace
        self.hasDeviceAggregatorProperty = hasDeviceAggregatorProperty
        self.includesDevice = includesDevice
        
        
class TimeseriesList(BIGGObjects):
    __rdf_type__ = Bigg.TimeseriesList

    def __init__(self, subject, comment=None,label=None,TimeSeriesEnd=None,TimeSeriesFrequency=None,TimeSeriesIsCumulative=None,TimeSeriesIsOnChange=None,TimeSeriesIsRegular=None,TimeSeriesStart=None,TimeSeriesTimeAggregationFunction=None,hasMeasuredProperty=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.TimeSeriesEnd = TimeSeriesEnd
        self.TimeSeriesFrequency = TimeSeriesFrequency
        self.TimeSeriesIsCumulative = TimeSeriesIsCumulative
        self.TimeSeriesIsOnChange = TimeSeriesIsOnChange
        self.TimeSeriesIsRegular = TimeSeriesIsRegular
        self.TimeSeriesStart = TimeSeriesStart
        self.TimeSeriesTimeAggregationFunction = TimeSeriesTimeAggregationFunction
        self.hasMeasuredProperty = hasMeasuredProperty
        
        
class AreaType(BIGGObjects):
    __rdf_type__ = Bigg.AreaType

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class AreaUnitOfMeasurement(BIGGObjects):
    __rdf_type__ = Bigg.AreaUnitOfMeasurement

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class BuildingConstructionElementType(BIGGObjects):
    __rdf_type__ = Bigg.BuildingConstructionElementType

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class BuildingSpaceUseType(BIGGObjects):
    __rdf_type__ = Bigg.BuildingSpaceUseType

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class BuildingSystemElementType(BIGGObjects):
    __rdf_type__ = Bigg.BuildingSystemElementType

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class EnergyEfficiencyMeasureInvestmentCurrency(BIGGObjects):
    __rdf_type__ = Bigg.EnergyEfficiencyMeasureInvestmentCurrency

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class EnergyEfficiencyMeasureType(BIGGObjects):
    __rdf_type__ = Bigg.EnergyEfficiencyMeasureType

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class IndoorQualityUserPerception(BIGGObjects):
    __rdf_type__ = Bigg.IndoorQualityUserPerception

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class MaintenanceActionType(BIGGObjects):
    __rdf_type__ = Bigg.MaintenanceActionType

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class Area(BIGGObjects):
    __rdf_type__ = Bigg.Area

    def __init__(self, subject, comment=None,label=None,areaValue=None,hasAreaType=None,hasAreaUnitOfMeasurement=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.areaValue = areaValue
        self.hasAreaType = hasAreaType
        self.hasAreaUnitOfMeasurement = hasAreaUnitOfMeasurement
        
        
class IndoorQualityPerception(BIGGObjects):
    __rdf_type__ = Bigg.IndoorQualityPerception

    def __init__(self, subject, comment=None,label=None,indoorQualityValidityEndDate=None,indoorQualityValidityStartDate=None,hasIndoorQualityUserPerception=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.indoorQualityValidityEndDate = indoorQualityValidityEndDate
        self.indoorQualityValidityStartDate = indoorQualityValidityStartDate
        self.hasIndoorQualityUserPerception = hasIndoorQualityUserPerception
        
        
class OccupancyProfile(BIGGObjects):
    __rdf_type__ = Bigg.OccupancyProfile

    def __init__(self, subject, comment=None,label=None,occupancyNumberOfOccupants=None,occupancyProfileValidityEndDate=None,occupancyProfileValidityStartDate=None,occupancyVacationDates=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.occupancyNumberOfOccupants = occupancyNumberOfOccupants
        self.occupancyProfileValidityEndDate = occupancyProfileValidityEndDate
        self.occupancyProfileValidityStartDate = occupancyProfileValidityStartDate
        self.occupancyVacationDates = occupancyVacationDates
        
        
class MaintenanceAction(BIGGObjects):
    __rdf_type__ = Bigg.MaintenanceAction

    def __init__(self, subject, comment=None,label=None,maintenanceActionDate=None,maintenanceActionDescription=None,maintenanceActionFrequency=None,maintenanceActionIsPeriodic=None,maintenanceActionName=None,hasMaintenanceActionType=None,isSubjectToMaintenance=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.maintenanceActionDate = maintenanceActionDate
        self.maintenanceActionDescription = maintenanceActionDescription
        self.maintenanceActionFrequency = maintenanceActionFrequency
        self.maintenanceActionIsPeriodic = maintenanceActionIsPeriodic
        self.maintenanceActionName = maintenanceActionName
        self.hasMaintenanceActionType = hasMaintenanceActionType
        self.isSubjectToMaintenance = isSubjectToMaintenance
        
        
class EnergyPerformanceCertificateAdditionalInfo(BIGGObjects):
    __rdf_type__ = Bigg.EnergyPerformanceCertificateAdditionalInfo

    def __init__(self, subject, comment=None,label=None,averageFacadeTransmittance=None,averageWindowsTransmittance=None,biomassSystemPresence=None,buildingTechnicalInspectionCode=None,constructionRegulation=None,districtHeatingOrCoolingConnection=None,electricVehicleChargerPresence=None,geothermalSystemPresence=None,regulationValueForFacadeTransmittance=None,regulationValueForWindowsTransmittance=None,solarPVSystemPresence=None,solarThermalSystemPresence=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.averageFacadeTransmittance = averageFacadeTransmittance
        self.averageWindowsTransmittance = averageWindowsTransmittance
        self.biomassSystemPresence = biomassSystemPresence
        self.buildingTechnicalInspectionCode = buildingTechnicalInspectionCode
        self.constructionRegulation = constructionRegulation
        self.districtHeatingOrCoolingConnection = districtHeatingOrCoolingConnection
        self.electricVehicleChargerPresence = electricVehicleChargerPresence
        self.geothermalSystemPresence = geothermalSystemPresence
        self.regulationValueForFacadeTransmittance = regulationValueForFacadeTransmittance
        self.regulationValueForWindowsTransmittance = regulationValueForWindowsTransmittance
        self.solarPVSystemPresence = solarPVSystemPresence
        self.solarThermalSystemPresence = solarThermalSystemPresence
        
        
class EnergyPerformanceCertificate(BIGGObjects):
    __rdf_type__ = Bigg.EnergyPerformanceCertificate

    def __init__(self, subject, comment=None,label=None,C02EmissionsClass=None,annualC02Emissions=None,annualEnergyCost=None,annualFinalEnergyConsumption=None,annualHeatingCO2Emissions=None,annualHeatingEnergyDemand=None,annualHeatingPrimaryEnergyConsumption=None,annualLightingCO2Emissions=None,annualPrimaryEnergyConsumption=None,energyPerformanceCertificateReferenceNumber=None,energyPerformanceCertificationMotivation=None,energyPerformanceCertificationTool=None,energyPerformanceClass=None,energyPerformanceDateOfAssessment=None,energyPerformanceDateOfCertification=None,energyPerformanceProcedureType=None,heatingCO2EmissionsClass=None,heatingPrimaryEnergyClass=None,lightingCO2EmissionsClass=None,lightingPrimaryEnergyClass=None,lightingPrimaryEnergyConsumption=None,hasAdditionalInfo=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.C02EmissionsClass = C02EmissionsClass
        self.annualC02Emissions = annualC02Emissions
        self.annualEnergyCost = annualEnergyCost
        self.annualFinalEnergyConsumption = annualFinalEnergyConsumption
        self.annualHeatingCO2Emissions = annualHeatingCO2Emissions
        self.annualHeatingEnergyDemand = annualHeatingEnergyDemand
        self.annualHeatingPrimaryEnergyConsumption = annualHeatingPrimaryEnergyConsumption
        self.annualLightingCO2Emissions = annualLightingCO2Emissions
        self.annualPrimaryEnergyConsumption = annualPrimaryEnergyConsumption
        self.energyPerformanceCertificateReferenceNumber = energyPerformanceCertificateReferenceNumber
        self.energyPerformanceCertificationMotivation = energyPerformanceCertificationMotivation
        self.energyPerformanceCertificationTool = energyPerformanceCertificationTool
        self.energyPerformanceClass = energyPerformanceClass
        self.energyPerformanceDateOfAssessment = energyPerformanceDateOfAssessment
        self.energyPerformanceDateOfCertification = energyPerformanceDateOfCertification
        self.energyPerformanceProcedureType = energyPerformanceProcedureType
        self.heatingCO2EmissionsClass = heatingCO2EmissionsClass
        self.heatingPrimaryEnergyClass = heatingPrimaryEnergyClass
        self.lightingCO2EmissionsClass = lightingCO2EmissionsClass
        self.lightingPrimaryEnergyClass = lightingPrimaryEnergyClass
        self.lightingPrimaryEnergyConsumption = lightingPrimaryEnergyConsumption
        self.hasAdditionalInfo = hasAdditionalInfo
        
        
class SystemType(BIGGObjects):
    __rdf_type__ = Bigg.SystemType

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class ZoneType(BIGGObjects):
    __rdf_type__ = Bigg.ZoneType

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class Group(BIGGObjects):
    __rdf_type__ = Bigg.Group

    def __init__(self, subject, comment=None,label=None,groupName=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.groupName = groupName
        
        
class EnergySavingType(BIGGObjects):
    __rdf_type__ = Bigg.EnergySavingType

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class EnergySavingVerificationSource(BIGGObjects):
    __rdf_type__ = Bigg.EnergySavingVerificationSource

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class NonEnergyBenefitImpactEvaluation(BIGGObjects):
    __rdf_type__ = Bigg.NonEnergyBenefitImpactEvaluation

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class NonEnergyBenefitImpactValueUnit(BIGGObjects):
    __rdf_type__ = Bigg.NonEnergyBenefitImpactValueUnit

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class NonEnergyBenefitType(BIGGObjects):
    __rdf_type__ = Bigg.NonEnergyBenefitType

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class ProjectInvestmentCurrency(BIGGObjects):
    __rdf_type__ = Bigg.ProjectInvestmentCurrency

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class ProjectMotivation(BIGGObjects):
    __rdf_type__ = Bigg.ProjectMotivation

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class NonEnergyBenefitProducingItem(BIGGObjects):
    __rdf_type__ = Bigg.NonEnergyBenefitProducingItem

    def __init__(self, subject, comment=None,label=None,producesNonEnergyBenefit=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.producesNonEnergyBenefit = producesNonEnergyBenefit
        
        
class SavingProducingItem(BIGGObjects):
    __rdf_type__ = Bigg.SavingProducingItem

    def __init__(self, subject, comment=None,label=None,producesSaving=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.producesSaving = producesSaving
        
        
class NonEnergyBenefit(BIGGObjects):
    __rdf_type__ = Bigg.NonEnergyBenefit

    def __init__(self, subject, comment=None,label=None,nonEnergyBenefitImpactValue=None,nonEnergyBenefitImpactValueDescription=None,nonEnergyBenefitImpactValueVerifiedAndMeasured=None,nonEnergyBenefitImpactVerificationMethod=None,hasNonEnergyBenefitImpactEvaluation=None,hasNonEnergyBenefitImpactValueUnit=None,hasNonEnergyBenefitType=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.nonEnergyBenefitImpactValue = nonEnergyBenefitImpactValue
        self.nonEnergyBenefitImpactValueDescription = nonEnergyBenefitImpactValueDescription
        self.nonEnergyBenefitImpactValueVerifiedAndMeasured = nonEnergyBenefitImpactValueVerifiedAndMeasured
        self.nonEnergyBenefitImpactVerificationMethod = nonEnergyBenefitImpactVerificationMethod
        self.hasNonEnergyBenefitImpactEvaluation = hasNonEnergyBenefitImpactEvaluation
        self.hasNonEnergyBenefitImpactValueUnit = hasNonEnergyBenefitImpactValueUnit
        self.hasNonEnergyBenefitType = hasNonEnergyBenefitType
        
        
class EnergySaving(BIGGObjects):
    __rdf_type__ = Bigg.EnergySaving

    def __init__(self, subject, comment=None,label=None,energySavingEndDate=None,energySavingIndependentlyVerified=None,energySavingStartDate=None,energySavingValue=None,hasEnergySavingType=None,hasEnergySavingVerificationSource=None,influencesObjective=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.energySavingEndDate = energySavingEndDate
        self.energySavingIndependentlyVerified = energySavingIndependentlyVerified
        self.energySavingStartDate = energySavingStartDate
        self.energySavingValue = energySavingValue
        self.hasEnergySavingType = hasEnergySavingType
        self.hasEnergySavingVerificationSource = hasEnergySavingVerificationSource
        self.influencesObjective = influencesObjective
        
        
class TariffCurrency(BIGGObjects):
    __rdf_type__ = Bigg.TariffCurrency

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class ContractedTariff(BIGGObjects):
    __rdf_type__ = Bigg.ContractedTariff

    def __init__(self, subject, comment=None,label=None,hasTariff=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.hasTariff = hasTariff
        