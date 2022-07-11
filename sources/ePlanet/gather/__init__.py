import argparse

import pandas as pd

COLUMN_NAMES = ['Year', 'Month', 'Code', 'Municipality Unit', 'Municipality', 'Region', 'Office', 'Meter id',
                'Bill num', 'Bill num 2', 'Name', 'Street', 'Street num', 'City', 'Bill Issuing Day', 'Month1', 'Year1',
                'Meter Code', 'Type Of Building', 'Current Record', 'Previous Record', 'Variable', 'Recording Date',
                'Previous Recording Date', 'Electricity Consumtion', 'Municiaplity Unit 1']


def gather_data(config, settings, args):
    df = pd.read_excel('data/ePlanet/sample of the translations in the energy data of the municipality .xlsx',
                       skiprows=5)


def gather(arguments, config=None, settings=None):
    ap = argparse.ArgumentParser(description='Gathering data from Nedgia')
    ap.add_argument("-st", "--store", required=True, help="Where to store the data", choices=["kafka", "hbase"])
    ap.add_argument("--user", "-u", help="The user importing the data", required=True)
    ap.add_argument("--namespace", "-n", help="The subjects namespace uri", required=True)
    ap.add_argument("-f", "--file", required=True, help="Excel file path to parse")
    args = ap.parse_args(arguments)

    gather_data(config=config, settings=settings, args=args)
