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
        for tt in self.__rdf_type__:
            g.add((self.subject, RDF.type, tt))
        for k, v in vars(self).items():
            if k != "subject" and v:
                if isinstance(v, URIRef):
                    g.add((self.subject, Bigg[k], v))
                else:
                    g.add((self.subject, Bigg[k], Literal(v)))
        return g
    
        
class AddressCity(BIGGObjects):
    __rdf_type__ = ['AddressCity', 'Feature', 'Thing']

    def __init__(self, subject, name=None,comment=None,label=None):
        super().__init__(subject)
        self.name = name
        self.comment = comment
        self.label = label
        
        
class AddressCountry(BIGGObjects):
    __rdf_type__ = ['AddressCountry', 'Feature', 'Thing']

    def __init__(self, subject, name=None,comment=None,label=None):
        super().__init__(subject)
        self.name = name
        self.comment = comment
        self.label = label
        
        
class AddressProvince(BIGGObjects):
    __rdf_type__ = ['AddressProvince', 'Feature', 'Thing']

    def __init__(self, subject, name=None,comment=None,label=None):
        super().__init__(subject)
        self.name = name
        self.comment = comment
        self.label = label
        
        
class EnergyPerformanceContract(BIGGObjects):
    __rdf_type__ = ['EnergyPerformanceContract', 'Contract', 'Thing']

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
    __rdf_type__ = ['Element', 'ObservableItem', 'Thing']

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
    __rdf_type__ = ['Measurement', 'TimeseriesPoint', 'Thing']

    def __init__(self, subject, comment=None,label=None,end=None,isReal=None,start=None,value=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.end = end
        self.isReal = isReal
        self.start = start
        self.value = value
        
        
class StatePoint(BIGGObjects):
    __rdf_type__ = ['StatePoint', 'TimeseriesPoint', 'Thing']

    def __init__(self, subject, comment=None,label=None,end=None,isReal=None,start=None,value=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.end = end
        self.isReal = isReal
        self.start = start
        self.value = value
        
        
class WeatherStation(BIGGObjects):
    __rdf_type__ = ['WeatherStation', 'DataProvider', 'Thing']

    def __init__(self, subject, comment=None,label=None,latitude=None,longitude=None,hasDeviceInputProtocol=None,hasDeviceInputSignalType=None,hasDeviceType=None,hasHistory=None,hasSensor=None,hasState=None,hasUtilityPointofDelivery=None,isPartOfDeviceAggregator=None,observes=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
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
    __rdf_type__ = ['State', 'TimeseriesList', 'Thing']

    def __init__(self, subject, comment=None,label=None,timeSeriesEnd=None,timeSeriesFrequency=None,timeSeriesIsCumulative=None,timeSeriesIsOnChange=None,timeSeriesIsRegular=None,timeSeriesStart=None,timeSeriesTimeAggregationFunction=None,hasMeasuredProperty=None,hasStatePoint=None,hasStateType=None,hasStateUnit=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.timeSeriesEnd = timeSeriesEnd
        self.timeSeriesFrequency = timeSeriesFrequency
        self.timeSeriesIsCumulative = timeSeriesIsCumulative
        self.timeSeriesIsOnChange = timeSeriesIsOnChange
        self.timeSeriesIsRegular = timeSeriesIsRegular
        self.timeSeriesStart = timeSeriesStart
        self.timeSeriesTimeAggregationFunction = timeSeriesTimeAggregationFunction
        self.hasMeasuredProperty = hasMeasuredProperty
        self.hasStatePoint = hasStatePoint
        self.hasStateType = hasStateType
        self.hasStateUnit = hasStateUnit
        
        
class BuildingSpace(BIGGObjects):
    __rdf_type__ = ['BuildingSpace', 'ObservableItem', 'Thing']

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
    __rdf_type__ = ['Sensor', 'TimeseriesList', 'Thing']

    def __init__(self, subject, comment=None,label=None,timeSeriesEnd=None,timeSeriesFrequency=None,timeSeriesIsCumulative=None,timeSeriesIsOnChange=None,timeSeriesIsRegular=None,timeSeriesStart=None,timeSeriesTimeAggregationFunction=None,hasMeasuredProperty=None,hasMeasurement=None,hasMeasurementUnit=None,hasOutputProtocol=None,hasOutputSignalType=None,hasSensorEstimationMethod=None,hasSensorReadingType=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.timeSeriesEnd = timeSeriesEnd
        self.timeSeriesFrequency = timeSeriesFrequency
        self.timeSeriesIsCumulative = timeSeriesIsCumulative
        self.timeSeriesIsOnChange = timeSeriesIsOnChange
        self.timeSeriesIsRegular = timeSeriesIsRegular
        self.timeSeriesStart = timeSeriesStart
        self.timeSeriesTimeAggregationFunction = timeSeriesTimeAggregationFunction
        self.hasMeasuredProperty = hasMeasuredProperty
        self.hasMeasurement = hasMeasurement
        self.hasMeasurementUnit = hasMeasurementUnit
        self.hasOutputProtocol = hasOutputProtocol
        self.hasOutputSignalType = hasOutputSignalType
        self.hasSensorEstimationMethod = hasSensorEstimationMethod
        self.hasSensorReadingType = hasSensorReadingType
        
        
class Device(BIGGObjects):
    __rdf_type__ = ['Device', 'DataProvider', 'Element', 'Thing']

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
    __rdf_type__ = ['BuildingConstructionElement', 'BuildingElement', 'Thing']

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
    __rdf_type__ = ['BuildingSystemElement', 'BuildingElement', 'Thing']

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
    __rdf_type__ = ['BuildingElement', 'Element', 'Thing']

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
    __rdf_type__ = ['EnergyEfficiencyMeasure', 'NonEnergyBenefitProducingItem', 'SavingProducingItem', 'Thing']

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
    __rdf_type__ = ['System', 'Group', 'Thing']

    def __init__(self, subject, comment=None,label=None,groupName=None,hasSystemType=None,isContainedInSystem=None,servesZone=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.groupName = groupName
        self.hasSystemType = hasSystemType
        self.isContainedInSystem = isContainedInSystem
        self.servesZone = servesZone
        
        
class Zone(BIGGObjects):
    __rdf_type__ = ['Zone', 'Group', 'Thing']

    def __init__(self, subject, comment=None,label=None,groupName=None,hasZoneType=None,isContainedInZone=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.groupName = groupName
        self.hasZoneType = hasZoneType
        self.isContainedInZone = isContainedInZone
        
        
class RenovationProject(BIGGObjects):
    __rdf_type__ = ['RenovationProject', 'Project', 'Thing']

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
    __rdf_type__ = ['RetrofitProject', 'Project', 'Thing']

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
    __rdf_type__ = ['Project', 'NonEnergyBenefitProducingItem', 'SavingProducingItem', 'Thing']

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
    __rdf_type__ = ['CO2EmissionsPoint', 'TimeseriesPoint', 'Thing']

    def __init__(self, subject, comment=None,label=None,end=None,isReal=None,start=None,value=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.end = end
        self.isReal = isReal
        self.start = start
        self.value = value
        
        
class TariffPoint(BIGGObjects):
    __rdf_type__ = ['TariffPoint', 'TimeseriesPoint', 'Thing']

    def __init__(self, subject, comment=None,label=None,end=None,isReal=None,start=None,value=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.end = end
        self.isReal = isReal
        self.start = start
        self.value = value
        
        
class CO2EmissionsFactorList(BIGGObjects):
    __rdf_type__ = ['CO2EmissionsFactorList', 'TimeseriesList', 'Thing']

    def __init__(self, subject, comment=None,label=None,timeSeriesEnd=None,timeSeriesFrequency=None,timeSeriesIsCumulative=None,timeSeriesIsOnChange=None,timeSeriesIsRegular=None,timeSeriesStart=None,timeSeriesTimeAggregationFunction=None,hasMeasuredProperty=None,hasCO2EmissionsFactorValue=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.timeSeriesEnd = timeSeriesEnd
        self.timeSeriesFrequency = timeSeriesFrequency
        self.timeSeriesIsCumulative = timeSeriesIsCumulative
        self.timeSeriesIsOnChange = timeSeriesIsOnChange
        self.timeSeriesIsRegular = timeSeriesIsRegular
        self.timeSeriesStart = timeSeriesStart
        self.timeSeriesTimeAggregationFunction = timeSeriesTimeAggregationFunction
        self.hasMeasuredProperty = hasMeasuredProperty
        self.hasCO2EmissionsFactorValue = hasCO2EmissionsFactorValue
        
        
class ContractedTariff(BIGGObjects):
    __rdf_type__ = ['ContractedTariff', 'Contract', 'Thing']

    def __init__(self, subject, contractEndDate=None,contractName=None,contractStartDate=None,comment=None,label=None,hasTariff=None):
        super().__init__(subject)
        self.contractEndDate = contractEndDate
        self.contractName = contractName
        self.contractStartDate = contractStartDate
        self.comment = comment
        self.label = label
        self.hasTariff = hasTariff
        
        
class TariffPrice(BIGGObjects):
    __rdf_type__ = ['TariffPrice', 'TimeseriesList', 'Thing']

    def __init__(self, subject, comment=None,label=None,timeSeriesEnd=None,timeSeriesFrequency=None,timeSeriesIsCumulative=None,timeSeriesIsOnChange=None,timeSeriesIsRegular=None,timeSeriesStart=None,timeSeriesTimeAggregationFunction=None,hasMeasuredProperty=None,hasTariffValues=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.timeSeriesEnd = timeSeriesEnd
        self.timeSeriesFrequency = timeSeriesFrequency
        self.timeSeriesIsCumulative = timeSeriesIsCumulative
        self.timeSeriesIsOnChange = timeSeriesIsOnChange
        self.timeSeriesIsRegular = timeSeriesIsRegular
        self.timeSeriesStart = timeSeriesStart
        self.timeSeriesTimeAggregationFunction = timeSeriesTimeAggregationFunction
        self.hasMeasuredProperty = hasMeasuredProperty
        self.hasTariffValues = hasTariffValues
        
        
class AddressClimateZone(BIGGObjects):
    __rdf_type__ = ['AddressClimateZone', 'Thing']

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class BuildingConstructionType(BIGGObjects):
    __rdf_type__ = ['BuildingConstructionType', 'Thing']

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class BuildingOwnership(BIGGObjects):
    __rdf_type__ = ['BuildingOwnership', 'Thing']

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class LandType(BIGGObjects):
    __rdf_type__ = ['LandType', 'Thing']

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class ObjectiveTargetType(BIGGObjects):
    __rdf_type__ = ['ObjectiveTargetType', 'Thing']

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class ObjectiveTargetUnit(BIGGObjects):
    __rdf_type__ = ['ObjectiveTargetUnit', 'Thing']

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class OrganiationType(BIGGObjects):
    __rdf_type__ = ['OrganiationType', 'Thing']

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class Contract(BIGGObjects):
    __rdf_type__ = ['Contract', 'Thing']

    def __init__(self, subject, contractEndDate=None,contractName=None,contractStartDate=None,comment=None,label=None):
        super().__init__(subject)
        self.contractEndDate = contractEndDate
        self.contractName = contractName
        self.contractStartDate = contractStartDate
        self.comment = comment
        self.label = label
        
        
class Feature(BIGGObjects):
    __rdf_type__ = ['Feature', 'Thing']

    def __init__(self, subject, name=None,comment=None,label=None):
        super().__init__(subject)
        self.name = name
        self.comment = comment
        self.label = label
        
        
class CadastralInfo(BIGGObjects):
    __rdf_type__ = ['CadastralInfo', 'Thing']

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
    __rdf_type__ = ['EnergyPerformanceContractObjective', 'Thing']

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
    __rdf_type__ = ['Person', 'Thing']

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
    __rdf_type__ = ['Building', 'Thing']

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
    __rdf_type__ = ['LocationInfo', 'Thing']

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
    __rdf_type__ = ['Organization', 'Thing']

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
        
        
class ObservableDataProvider(BIGGObjects):
    __rdf_type__ = ['ObservableDataProvider', 'Thing']

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class DeviceInputProtocol(BIGGObjects):
    __rdf_type__ = ['DeviceInputProtocol', 'Thing']

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class DeviceInputSignalType(BIGGObjects):
    __rdf_type__ = ['DeviceInputSignalType', 'Thing']

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class DeviceType(BIGGObjects):
    __rdf_type__ = ['DeviceType', 'Thing']

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class OutputProtocol(BIGGObjects):
    __rdf_type__ = ['OutputProtocol', 'Thing']

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class OutputSignalType(BIGGObjects):
    __rdf_type__ = ['OutputSignalType', 'Thing']

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class SensorEstimationMethod(BIGGObjects):
    __rdf_type__ = ['SensorEstimationMethod', 'Thing']

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class SensorReadingType(BIGGObjects):
    __rdf_type__ = ['SensorReadingType', 'Thing']

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class StateType(BIGGObjects):
    __rdf_type__ = ['StateType', 'Thing']

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class UtilityType(BIGGObjects):
    __rdf_type__ = ['UtilityType', 'Thing']

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class DeviceHistory(BIGGObjects):
    __rdf_type__ = ['DeviceHistory', 'Thing']

    def __init__(self, subject, comment=None,label=None,containsHistoryDevices=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.containsHistoryDevices = containsHistoryDevices
        
        
class MeasuredProperty(BIGGObjects):
    __rdf_type__ = ['MeasuredProperty', 'Thing']

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class MeasurementUnit(BIGGObjects):
    __rdf_type__ = ['MeasurementUnit', 'Thing']

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class UtilityPointOfDelivery(BIGGObjects):
    __rdf_type__ = ['UtilityPointOfDelivery', 'Thing']

    def __init__(self, subject, comment=None,label=None,pointOfDeliveryIDFromOrganization=None,hasUtilityType=None,hasCO2EmissionsFactor=None,hasContractedTariff=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.pointOfDeliveryIDFromOrganization = pointOfDeliveryIDFromOrganization
        self.hasUtilityType = hasUtilityType
        self.hasCO2EmissionsFactor = hasCO2EmissionsFactor
        self.hasContractedTariff = hasContractedTariff
        
        
class ObservableItem(BIGGObjects):
    __rdf_type__ = ['ObservableItem', 'Thing']

    def __init__(self, subject, comment=None,label=None,isObservedByDevice=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.isObservedByDevice = isObservedByDevice
        
        
class TimeseriesPoint(BIGGObjects):
    __rdf_type__ = ['TimeseriesPoint', 'Thing']

    def __init__(self, subject, comment=None,label=None,end=None,isReal=None,start=None,value=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.end = end
        self.isReal = isReal
        self.start = start
        self.value = value
        
        
class DeviceAggregator(BIGGObjects):
    __rdf_type__ = ['DeviceAggregator', 'Thing']

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
    __rdf_type__ = ['TimeseriesList', 'Thing']

    def __init__(self, subject, comment=None,label=None,timeSeriesEnd=None,timeSeriesFrequency=None,timeSeriesIsCumulative=None,timeSeriesIsOnChange=None,timeSeriesIsRegular=None,timeSeriesStart=None,timeSeriesTimeAggregationFunction=None,hasMeasuredProperty=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.timeSeriesEnd = timeSeriesEnd
        self.timeSeriesFrequency = timeSeriesFrequency
        self.timeSeriesIsCumulative = timeSeriesIsCumulative
        self.timeSeriesIsOnChange = timeSeriesIsOnChange
        self.timeSeriesIsRegular = timeSeriesIsRegular
        self.timeSeriesStart = timeSeriesStart
        self.timeSeriesTimeAggregationFunction = timeSeriesTimeAggregationFunction
        self.hasMeasuredProperty = hasMeasuredProperty
        
        
class DataProvider(BIGGObjects):
    __rdf_type__ = ['DataProvider', 'Thing']

    def __init__(self, subject, comment=None,label=None,hasDeviceInputProtocol=None,hasDeviceInputSignalType=None,hasDeviceType=None,hasHistory=None,hasSensor=None,hasState=None,hasUtilityPointofDelivery=None,isPartOfDeviceAggregator=None,observes=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.hasDeviceInputProtocol = hasDeviceInputProtocol
        self.hasDeviceInputSignalType = hasDeviceInputSignalType
        self.hasDeviceType = hasDeviceType
        self.hasHistory = hasHistory
        self.hasSensor = hasSensor
        self.hasState = hasState
        self.hasUtilityPointofDelivery = hasUtilityPointofDelivery
        self.isPartOfDeviceAggregator = isPartOfDeviceAggregator
        self.observes = observes
        
        
class AreaType(BIGGObjects):
    __rdf_type__ = ['AreaType', 'Thing']

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class AreaUnitOfMeasurement(BIGGObjects):
    __rdf_type__ = ['AreaUnitOfMeasurement', 'Thing']

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class BuildingConstructionElementType(BIGGObjects):
    __rdf_type__ = ['BuildingConstructionElementType', 'Thing']

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class BuildingSpaceUseType(BIGGObjects):
    __rdf_type__ = ['BuildingSpaceUseType', 'Thing']

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class BuildingSystemElementType(BIGGObjects):
    __rdf_type__ = ['BuildingSystemElementType', 'Thing']

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class EnergyEfficiencyMeasureInvestmentCurrency(BIGGObjects):
    __rdf_type__ = ['EnergyEfficiencyMeasureInvestmentCurrency', 'Thing']

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class EnergyEfficiencyMeasureType(BIGGObjects):
    __rdf_type__ = ['EnergyEfficiencyMeasureType', 'Thing']

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class IndoorQualityUserPerception(BIGGObjects):
    __rdf_type__ = ['IndoorQualityUserPerception', 'Thing']

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class MaintenanceActionType(BIGGObjects):
    __rdf_type__ = ['MaintenanceActionType', 'Thing']

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class Area(BIGGObjects):
    __rdf_type__ = ['Area', 'Thing']

    def __init__(self, subject, comment=None,label=None,areaValue=None,hasAreaType=None,hasAreaUnitOfMeasurement=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.areaValue = areaValue
        self.hasAreaType = hasAreaType
        self.hasAreaUnitOfMeasurement = hasAreaUnitOfMeasurement
        
        
class IndoorQualityPerception(BIGGObjects):
    __rdf_type__ = ['IndoorQualityPerception', 'Thing']

    def __init__(self, subject, comment=None,label=None,indoorQualityValidityEndDate=None,indoorQualityValidityStartDate=None,hasIndoorQualityUserPerception=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.indoorQualityValidityEndDate = indoorQualityValidityEndDate
        self.indoorQualityValidityStartDate = indoorQualityValidityStartDate
        self.hasIndoorQualityUserPerception = hasIndoorQualityUserPerception
        
        
class OccupancyProfile(BIGGObjects):
    __rdf_type__ = ['OccupancyProfile', 'Thing']

    def __init__(self, subject, comment=None,label=None,occupancyNumberOfOccupants=None,occupancyProfileValidityEndDate=None,occupancyProfileValidityStartDate=None,occupancyVacationDates=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.occupancyNumberOfOccupants = occupancyNumberOfOccupants
        self.occupancyProfileValidityEndDate = occupancyProfileValidityEndDate
        self.occupancyProfileValidityStartDate = occupancyProfileValidityStartDate
        self.occupancyVacationDates = occupancyVacationDates
        
        
class MaintenanceAction(BIGGObjects):
    __rdf_type__ = ['MaintenanceAction', 'Thing']

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
    __rdf_type__ = ['EnergyPerformanceCertificateAdditionalInfo', 'Thing']

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
    __rdf_type__ = ['EnergyPerformanceCertificate', 'Thing']

    def __init__(self, subject, comment=None,label=None,C02EmissionsClass=None,annualC02Emissions=None,annualCoolingCO2Emissions=None,annualCoolingEnergyDemand=None,annualCoolingPrimaryEnergyConsumption=None,annualEnergyCost=None,annualFinalEnergyConsumption=None,annualHeatingCO2Emissions=None,annualHeatingEnergyDemand=None,annualHeatingPrimaryEnergyConsumption=None,annualHotWaterCO2Emissions=None,annualHotWaterPrimaryEnergyConsumption=None,annualLightingCO2Emissions=None,annualPrimaryEnergyConsumption=None,coolingCO2EmissionsClass=None,coolingEnergyDemandClass=None,coolingPrimaryEnergyClass=None,energyPerformanceCertificateReferenceNumber=None,energyPerformanceCertificationMotivation=None,energyPerformanceCertificationTool=None,energyPerformanceClass=None,energyPerformanceDateOfAssessment=None,energyPerformanceDateOfCertification=None,energyPerformanceProcedureType=None,heatingCO2EmissionsClass=None,heatingEnergyDemandClass=None,heatingPrimaryEnergyClass=None,hotWaterCO2EmissionsClass=None,hotWaterPrimaryEnergyClass=None,lightingCO2EmissionsClass=None,lightingPrimaryEnergyClass=None,lightingPrimaryEnergyConsumption=None,hasAdditionalInfo=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.C02EmissionsClass = C02EmissionsClass
        self.annualC02Emissions = annualC02Emissions
        self.annualCoolingCO2Emissions = annualCoolingCO2Emissions
        self.annualCoolingEnergyDemand = annualCoolingEnergyDemand
        self.annualCoolingPrimaryEnergyConsumption = annualCoolingPrimaryEnergyConsumption
        self.annualEnergyCost = annualEnergyCost
        self.annualFinalEnergyConsumption = annualFinalEnergyConsumption
        self.annualHeatingCO2Emissions = annualHeatingCO2Emissions
        self.annualHeatingEnergyDemand = annualHeatingEnergyDemand
        self.annualHeatingPrimaryEnergyConsumption = annualHeatingPrimaryEnergyConsumption
        self.annualHotWaterCO2Emissions = annualHotWaterCO2Emissions
        self.annualHotWaterPrimaryEnergyConsumption = annualHotWaterPrimaryEnergyConsumption
        self.annualLightingCO2Emissions = annualLightingCO2Emissions
        self.annualPrimaryEnergyConsumption = annualPrimaryEnergyConsumption
        self.coolingCO2EmissionsClass = coolingCO2EmissionsClass
        self.coolingEnergyDemandClass = coolingEnergyDemandClass
        self.coolingPrimaryEnergyClass = coolingPrimaryEnergyClass
        self.energyPerformanceCertificateReferenceNumber = energyPerformanceCertificateReferenceNumber
        self.energyPerformanceCertificationMotivation = energyPerformanceCertificationMotivation
        self.energyPerformanceCertificationTool = energyPerformanceCertificationTool
        self.energyPerformanceClass = energyPerformanceClass
        self.energyPerformanceDateOfAssessment = energyPerformanceDateOfAssessment
        self.energyPerformanceDateOfCertification = energyPerformanceDateOfCertification
        self.energyPerformanceProcedureType = energyPerformanceProcedureType
        self.heatingCO2EmissionsClass = heatingCO2EmissionsClass
        self.heatingEnergyDemandClass = heatingEnergyDemandClass
        self.heatingPrimaryEnergyClass = heatingPrimaryEnergyClass
        self.hotWaterCO2EmissionsClass = hotWaterCO2EmissionsClass
        self.hotWaterPrimaryEnergyClass = hotWaterPrimaryEnergyClass
        self.lightingCO2EmissionsClass = lightingCO2EmissionsClass
        self.lightingPrimaryEnergyClass = lightingPrimaryEnergyClass
        self.lightingPrimaryEnergyConsumption = lightingPrimaryEnergyConsumption
        self.hasAdditionalInfo = hasAdditionalInfo
        
        
class SystemType(BIGGObjects):
    __rdf_type__ = ['SystemType', 'Thing']

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class ZoneType(BIGGObjects):
    __rdf_type__ = ['ZoneType', 'Thing']

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class Group(BIGGObjects):
    __rdf_type__ = ['Group', 'Thing']

    def __init__(self, subject, comment=None,label=None,groupName=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.groupName = groupName
        
        
class EnergySavingType(BIGGObjects):
    __rdf_type__ = ['EnergySavingType', 'Thing']

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class EnergySavingVerificationSource(BIGGObjects):
    __rdf_type__ = ['EnergySavingVerificationSource', 'Thing']

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class NonEnergyBenefitImpactEvaluation(BIGGObjects):
    __rdf_type__ = ['NonEnergyBenefitImpactEvaluation', 'Thing']

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class NonEnergyBenefitImpactValueUnit(BIGGObjects):
    __rdf_type__ = ['NonEnergyBenefitImpactValueUnit', 'Thing']

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class NonEnergyBenefitType(BIGGObjects):
    __rdf_type__ = ['NonEnergyBenefitType', 'Thing']

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class ProjectInvestmentCurrency(BIGGObjects):
    __rdf_type__ = ['ProjectInvestmentCurrency', 'Thing']

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class ProjectMotivation(BIGGObjects):
    __rdf_type__ = ['ProjectMotivation', 'Thing']

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class NonEnergyBenefitProducingItem(BIGGObjects):
    __rdf_type__ = ['NonEnergyBenefitProducingItem', 'Thing']

    def __init__(self, subject, comment=None,label=None,producesNonEnergyBenefit=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.producesNonEnergyBenefit = producesNonEnergyBenefit
        
        
class SavingProducingItem(BIGGObjects):
    __rdf_type__ = ['SavingProducingItem', 'Thing']

    def __init__(self, subject, comment=None,label=None,producesSaving=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.producesSaving = producesSaving
        
        
class NonEnergyBenefit(BIGGObjects):
    __rdf_type__ = ['NonEnergyBenefit', 'Thing']

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
    __rdf_type__ = ['EnergySaving', 'Thing']

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
    __rdf_type__ = ['TariffCurrency', 'Thing']

    def __init__(self, subject, comment=None,label=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        
        
class CO2EmissionsFactor(BIGGObjects):
    __rdf_type__ = ['CO2EmissionsFactor', 'Thing']

    def __init__(self, subject, comment=None,label=None,hasCO2EmissionsFactor=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.hasCO2EmissionsFactor = hasCO2EmissionsFactor
        
        
class Tariff(BIGGObjects):
    __rdf_type__ = ['Tariff', 'Thing']

    def __init__(self, subject, comment=None,label=None,tariffCompany=None,tariffName=None,hasTariffPrice=None,tariffCurrencyUnit=None):
        super().__init__(subject)
        self.comment = comment
        self.label = label
        self.tariffCompany = tariffCompany
        self.tariffName = tariffName
        self.hasTariffPrice = hasTariffPrice
        self.tariffCurrencyUnit = tariffCurrencyUnit
        