import argparse
import openpyxl


def gather_data(config, settings, args):
    wb = openpyxl.load_workbook("data/prilojenie/Prilojenie_2_ERD_041-Reziume_ENG.xlsx")
    building_description = wb['Building Description']
    climate_zone = building_description['B3'].value


def gather(arguments, config=None, settings=None):
    ap = argparse.ArgumentParser(description='Gathering data from Nedgia')
    ap.add_argument("-st", "--store", required=True, help="Where to store the data", choices=["kafka", "hbase"])
    ap.add_argument("--user", "-u", help="The user importing the data", required=True)
    ap.add_argument("--namespace", "-n", help="The subjects namespace uri", required=True)
    ap.add_argument("-f", "--file", required=True, help="Excel file path to parse")
    args = ap.parse_args(arguments)

    gather_data(config=config, settings=settings, args=args)
