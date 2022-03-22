import pandas as pd


def harmonize_data(data, **kwargs):
    df = pd.DataFrame.from_records(data)
    df['Fecha inicio Docu. cálculo'] = df['Fecha inicio Docu. cálculo'].dt.strftime('%Y/%m/%d 00:%M:%S')  # ISO 8601
    df['Fecha fin Docu. cálculo'] = df['Fecha fin Docu. cálculo'].dt.strftime('%Y/%m/%d 23:%M:%S')  # ISO 8601

    df = df[['CUPS', 'Fecha inicio Docu. cálculo', 'Fecha fin Docu. cálculo', 'Consumo kWh ATR', 'Consumo kWh GLP']]
