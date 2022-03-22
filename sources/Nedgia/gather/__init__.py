import argparse
import pandas as pd

import os


def gather_data():
    for file in os.listdir('data/'):
        if file.endswith('.xlsx'):
            df = pd.read_excel('/home/pc/Escritorio/beegroup_importing_tool/data/Generalitat Extracción_2018.xlsx',
                               skiprows=2)  # todo: change way to get input
            df['Fecha inicio Docu. cálculo'] = df['Fecha inicio Docu. cálculo'].dt.strftime(
                '%Y/%m/%d 00:%M:%S')  # ISO 8601
            df['Fecha fin Docu. cálculo'] = df['Fecha fin Docu. cálculo'].dt.strftime('%Y/%m/%d 23:%M:%S')  # ISO 8601


def gather(arguments, config=None, settings=None):
    ap = argparse.ArgumentParser(description='Gathering data from Nedgia')
    ap.add_argument("-st", "--store", required=True, help="Where to store the data", choices=["kafka", "hbase"])
    args = ap.parse_args(arguments)
    gather_data()
