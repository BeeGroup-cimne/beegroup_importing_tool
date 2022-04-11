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
    commissioning_date = wb['C25'].value
    floor_area = wb['C26'].value
    gross_floor_area = wb['C27'].value
    heating_area = wb['C28'].value
    heating_volume = wb['C29'].value
    cooling_area = wb['C30'].value
    cooling_volume = wb['C31'].value
    number_of_floors_before = wb['C32'].value
    number_of_floors_after = wb['D32'].value
    number_of_inhabitants = wb['C33'].value


def gather_building_description(wb):
    climate_zone = wb['B3'].value
    type_of_construction = wb['B8'].value


def gather_consumption(wb):
    heavy_fuel_oil_t = wb['C11'].value
    diesel_oil_t = wb['C12'].value
    lpg_t = wb['C13'].value
    diesel_oil_2_t = wb['C14'].value
    natural_gas_t = wb['C15'].value
    coal_t = wb['C16'].value
    pellets_t = wb['C17'].value
    wood_t = wb['C18'].value
    other_t = wb['C19'].value
    heat_energy_t = wb['C20'].value
    electricity_t = wb['C21'].value

    heavy_fuel_oil_nm = wb['D11'].value
    diesel_oil_nm = wb['D12'].value
    lpg_nm = wb['D13'].value
    diesel_oil_2_nm = wb['D14'].value
    natural_gas_nm = wb['D15'].value
    coal_nm = wb['D16'].value
    pellets_nm = wb['D17'].value
    wood_nm = wb['D18'].value
    other_nm = wb['D19'].value
    heat_energy_nm = wb['D20'].value
    electricity_nm = wb['D21'].value

    heavy_fuel_oil_kWh = wb['E11'].value
    diesel_oil_kWh = wb['E12'].value
    lpg_kWh = wb['E13'].value
    diesel_oil_2_kWh = wb['E14'].value
    natural_gas_kWh = wb['E15'].value
    coal_kWh = wb['E16'].value
    pellets_kWh = wb['E17'].value
    wood_kWh = wb['E18'].value
    other_kWh = wb['E19'].value
    heat_energy_kWh = wb['E20'].value
    electricity_kWh = wb['E21'].value

    heavy_fuel_oil_kWh_t = wb['F11'].value
    diesel_oil_kWh_t = wb['F12'].value
    lpg_kWh_t = wb['F13'].value
    diesel_oil_2_kWh_t = wb['F14'].value
    natural_gas_kWh_t = wb['F15'].value
    coal_kWh_t = wb['F16'].value
    pellets_kWh_t = wb['F17'].value
    wood_kWh_t = wb['F18'].value
    other_kWh_t = wb['F19'].value
    heat_energy_kWh_t = wb['F20'].value
    electricity_kWh_t = wb['F21'].value

    heavy_fuel_oil_BGN_ton = wb['G11'].value
    diesel_oil_BGN_ton = wb['G12'].value
    lpg_BGN_ton = wb['G13'].value
    diesel_oil_2_BGN_ton = wb['G14'].value
    natural_gas_BGN_ton = wb['G15'].value
    coal_BGN_ton = wb['G16'].value
    pellets_BGN_ton = wb['G17'].value
    wood_BGN_ton = wb['G18'].value
    other_BGN_ton = wb['G19'].value
    heat_energy_BGN_ton = wb['G20'].value
    electricity_BGN_ton = wb['G21'].value

    heavy_fuel_oil_BGN_kWh = wb['H11'].value
    diesel_oil_BGN_kWh = wb['H12'].value
    lpg_BGN_kWh = wb['H13'].value
    diesel_oil_2_BGN_kWh = wb['H14'].value
    natural_gas_BGN_kWh = wb['H15'].value
    coal_BGN_kWh = wb['H16'].value
    pellets_BGN_kWh = wb['H17'].value
    wood_BGN_kWh = wb['H18'].value
    other_BGN_kWh = wb['H19'].value
    heat_energy_BGN_kWh = wb['H20'].value
    electricity_BGN_kWh = wb['H21'].value

    total = wb['E22'].value


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
