import argparse
import openpyxl
import re

EMAIL_REGEX = re.compile(r"[^@]+@[^@]+\.[^@]+")
PHONE_NUM_REGEX = re.compile(
    r"\(?\+[0-9]{1,3}\)? ?-?[0-9]{1,3} ?-?[0-9]{3,5} ?-?[0-9]{4}( ?-?[0-9]{3})? ?(\w{1,10}\s?\d{1,6})?")


def gather_contacts(wb):
    epc = wb['B2'].value  # EnergyPerformanceContract.contractID
    valid_until = wb['B3'].value  # EnergyPerformanceContract.contractEndDate
    building_type = wb['C14'].value  # Building.buildingType
    energy_class_before_ee_measures = wb['C17'].value  # EnergyPerformanceCertificate.energyPerformanceClass
    energy_class_after_ee_measures = wb['D17'].value  # EnergyPerformanceCertificate.energyPerformanceClass
    energy_consumption_before_ee_measures = wb['C18'].value  # EnergyPerformanceCertificate.annualFinalEnergyConsumption
    energy_consumption_after_ee_measures = wb['D18'].value  # EnergyPerformanceCertificate.annualFinalEnergyConsumption
    organization_type = wb['C19'].value  # Organization.organizationType
    organization_contact_info = wb['C20'].value

    organization_address = None
    organization_phone = None
    organization_email = None

    if organization_contact_info:
        if EMAIL_REGEX.match(organization_contact_info):
            organization_email = organization_contact_info

        elif PHONE_NUM_REGEX.match(organization_contact_info):
            organization_phone = organization_contact_info

        else:
            organization_address = organization_contact_info

    cadastral_ref = wb['C21'].value  # CadastralReference
    municipality = wb['C23'].value  # Location.municipality
    town = wb['C24'].value  # Location.city


def gather_building_description(wb):
    pass


def gather_consumption(wb):
    pass


def gather_savings(wb):
    pass


def gather_data(config, settings, args):
    wb = openpyxl.load_workbook("data/prilojenie/Prilojenie_2_ERD_041-Reziume_ENG.xlsx")
    gather_contacts(wb['Contacts'])
    gather_building_description(wb['Building Description'])
    gather_consumption(wb['Consumption'])
    gather_savings(wb['Savings 2'])


def gather(arguments, config=None, settings=None):
    ap = argparse.ArgumentParser(description='Gathering data from Nedgia')
    ap.add_argument("-st", "--store", required=True, help="Where to store the data", choices=["kafka", "hbase"])
    ap.add_argument("--user", "-u", help="The user importing the data", required=True)
    ap.add_argument("--namespace", "-n", help="The subjects namespace uri", required=True)
    ap.add_argument("-f", "--file", required=True, help="Excel file path to parse")
    args = ap.parse_args(arguments)

    gather_data(config=config, settings=settings, args=args)
