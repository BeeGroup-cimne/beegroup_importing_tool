import pandas as pd


def harmonize_data(data, **kwargs):
    namespace = kwargs['namespace']
    user = kwargs['user']
    config = kwargs['config']

    data = data[0]

    df_general_info = pd.DataFrame(data['general_info'])
    df_general_info.dropna(axis=1, how='all', inplace=True)

    epc_id = data['epc_id']

    df_distribution = pd.DataFrame(data['distribution'])
    df_distribution.dropna(axis=1, how='all', inplace=True)

    df_consumption = pd.DataFrame(data['consumption'])
    df_consumption.dropna(axis=1, how='all', inplace=True)

    df_measurements = pd.DataFrame(data['measurements'])
    df_measurements[['id', 'id_type']] = df_measurements['id'].str.split('~', expand=True)
    df_measurements.dropna(axis=1, how='all', inplace=True)

    df_total_annual_savings = pd.DataFrame(data['total_annual_savings'])
    df_total_annual_savings[['id', 'id_type']] = df_total_annual_savings['id'].str.split('~', expand=True)
    df_total_annual_savings.dropna(axis=1, how='all', inplace=True)
    energy_saved = data['energy_saved']
