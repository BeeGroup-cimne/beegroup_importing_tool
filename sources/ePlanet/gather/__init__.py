import argparse

import pandas as pd

COLUMN_NAMES = ['Year', 'Month', 'Code', 'Municipality Unit', 'Municipality', 'Region', 'Office', 'Meter num',
                'Bill num', 'Bill num 2', 'Name', 'Street', 'Street num', 'City', 'Bill Issuing Day', 'Month1', 'Year1',
                'Meter Code', 'Type Of Building', 'Current Record', 'Previous Record', 'Variable', 'Recording Date',
                'Previous Recording Date', 'Electricity Consumption', 'Electricity Cost', 'VAT', 'Other',
                'Prev payment',
                'Energy Value', 'VAT Prev Payment', 'EPT', 'Out service' 'Debit/Credit' 'ETMEAR' 'VAT ETMEAR',
                'Special TAX',
                'TAX',
                'Low VAT',
                'High VAT', 'Intermediate Value', 'Total Energy Value', 'Total VAT of electricity',
                'Total VAT Services', 'Total VAT', 'Total ERT', 'Municipal TAX', 'Total TAP',
                'EETIDE', 'Total Account', 'Total Current Month', 'Account Type',
                'Municiaplity Unit 1']


def gather_data(config, settings, args):
    df = pd.read_excel('data/ePlanet/sample of the translations in the energy data of the municipality .xlsx',
                       skiprows=7, header=None, names=COLUMN_NAMES, index_col=None)


def gather(arguments, config=None, settings=None):
    ap = argparse.ArgumentParser(description='Gathering data from Nedgia')
    ap.add_argument("-st", "--store", required=True, help="Where to store the data", choices=["kafka", "hbase"])
    ap.add_argument("--user", "-u", help="The user importing the data", required=True)
    ap.add_argument("--namespace", "-n", help="The subjects namespace uri", required=True)
    ap.add_argument("-f", "--file", required=True, help="Excel file path to parse")
    args = ap.parse_args(arguments)

    gather_data(config=config, settings=settings, args=args)
