import argparse
import openpyxl
import re
from string import ascii_uppercase

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
    header_names = "t	Nm3	kWh	kWh/t  kWh/Nm3	BGN/ton BGN/Nm3	BGN/kWh".split("\t")
    rows_names = ["Heavy fuel oil",
                  "Diesel oil",
                  "LPG",
                  "Diesel oil 2",
                  "Natural gas",
                  "Coal",
                  "Pellets",
                  "Wood",
                  "Other (specify)",
                  "Heat energy",
                  "Electricity"
                  ]
    consumptions = {}
    init_row = 11
    for index, letter in enumerate(ascii_uppercase[2:8]):
        for index2 in range(init_row, init_row + len(rows_names)):
            consumptions.update(
                {f"{header_names[index]}_{rows_names[index2 - init_row]}": wb[f"{letter}{index2}"].value})

    total_consumption = wb['E22'].value

    distribution = {}
    header_names = ["Actual Specific", "Actual Total", "Corrected Specific", "Corrected Total", "Expected Specific",
                    'Expected Total']
    rows_names = ["Heating",
                  "Ventilation",
                  "DHW",
                  "Fans and pumps",
                  "Lighting",
                  "Appliances",
                  "Cooling",
                  "Total",
                  ]

    init_row = 29
    for index, letter in enumerate(ascii_uppercase[2:8]):
        for index2 in range(init_row, init_row + len(rows_names)):
            distribution.update(
                {f"{header_names[index]}_{rows_names[index2 - init_row]}": wb[f"{letter}{index2}"].value})


def gather_savings(wb):
    measurements = {}
    header_names = "t/a	Nm3/a.	kWh/a.	BGN/a	BGN	year	CO2 t/a".split('\t')
    rows_names = ["Heavy fuel oil",
                  "Diesel oil",
                  "LPG",
                  "Diesel oil 2",
                  "Natural gas",
                  "Coal",
                  "Pellets",
                  "Wood",
                  "Other (specify)",
                  "Heat energy",
                  "Electricity",
                  "Total Measure"
                  ]
    init_row = 7
    for it in range(5):
        init = init_row + (len(rows_names) * it)
        measurements[it + 1] = {}
        for index, letter in enumerate(ascii_uppercase[4:11]):
            for index2 in range(init, init + len(rows_names)):
                measurements[it + 1].update(
                    {f"{header_names[index]}_{rows_names[index2 - init]}": wb[f"{letter}{index2}"].value})

    init = 71
    measurements[6] = {}
    for index, letter in enumerate(ascii_uppercase[4:11]):
        for index2 in range(init, init + len(rows_names)):
            measurements[6].update(
                {f"{header_names[index]}_{rows_names[index2 - init]}": wb[f"{letter}{index2}"].value})

    init_row = 86
    for it in range(7, 11):
        init = init_row + (len(rows_names) * it)
        measurements[it] = {}
        for index, letter in enumerate(ascii_uppercase[4:11]):
            for index2 in range(init, init + len(rows_names)):
                measurements[it].update(
                    {f"{header_names[index]}_{rows_names[index2 - init]}": wb[f"{letter}{index2}"].value})

    init_row = 137
    for it in range(11, 15):
        init = init_row + (len(rows_names) * it)
        measurements[it] = {}
        for index, letter in enumerate(ascii_uppercase[4:11]):
            for index2 in range(init, init + len(rows_names)):
                measurements[it].update(
                    {f"{header_names[index]}_{rows_names[index2 - init]}": wb[f"{letter}{index2}"].value})


def gather_data(config, settings, args):
    wb = openpyxl.load_workbook("data/prilojenie/Prilojenie_2_ERD_041-Reziume_ENG.xlsx", data_only=True)
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
