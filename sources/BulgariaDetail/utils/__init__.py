from functools import partial

from harmonizer.cache import Cache
from utils.data_transformations import to_object_property, fuzz_location, get_taxonomy_mapping
from utils.rdf_utils.ontology.namespaces_definition import bigg_enums


def set_taxonomy(df, column):
    df['buildingSpaceUseType'] = df[column].map(get_taxonomy_mapping(
        taxonomy_file="sources/Bulgaria/harmonizer/TAX_BULGARIA.xlsx",
        default="Other")).apply(partial(to_object_property,
                                        namespace=bigg_enums))


def set_municipality(df, column):
    municipality_map = fuzz_location(Cache.municipality_dic_BG, ['ns1:name', 'ns1:shortName'],
                                     df[column].unique())
    df.loc[:, 'hasAddressCity'] = df[column].map(municipality_map)



# def clean_dataframe_eem_savings(df, eems_parted, start_column):
#     df['subject'] = df['epc_id']
#     df['element_subject'] = df['subject'].apply(construction_element_subject)
#     df['epc_date'] = pd.to_datetime(df['epc_date'], infer_datetime_format=True)
#     df['epc_date_before'] = df['epc_date'] - timedelta(days=365)
#     df['epc_date'] = (df['epc_date'].astype('datetime64')).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
#     df['epc_date_before'] = (df['epc_date_before'].astype('datetime64')).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
#     saving_columns = []
#     for i, eem_type in enumerate(eems_parted):
#         list_i = i + start_column
#         df[f"eem_{list_i}_subject"] = df['subject'].apply(lambda x: f"{x}-{eem_type}").apply(eem_subject)
#         for j, e_saving_type in enumerate(enum_energy_saving_type):
#             df_t = df['subject'].apply(lambda x: f"{x}-{eem_type}-{e_saving_type}").apply(energy_saving_subject)
#             df_t.name = f"energy_saving_{list_i}_{j}_subject"
#             saving_columns.append(df_t)
#     df = pd.concat([df] + saving_columns, axis=1)
#     return df[['subject', 'element_subject', 'epc_date_before', 'epc_date'] +
#               [x for x in df.columns if re.match("eem_.*_subject", x)] +
#               [x for x in df.columns if re.match("measurement_.*", x)] +
#               [x for x in df.columns if re.match("energy_saving_.*_subject", x)]]


# def clean_dataframe_project(df):
#     df['subject'] = df['epc_id']
#     df['project_subject'] = df['subject'].apply(project_subject)
#     df['epc_date'] = pd.to_datetime(df['epc_date'], infer_datetime_format=True)
#     df['epc_date_before'] = df['epc_date'] - timedelta(days=365)
#     df['epc_date'] = (df['epc_date'].astype('datetime64')).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
#     df['epc_date_before'] = (df['epc_date_before'].astype('datetime64')).dt.strftime("%Y-%m-%dT%H:%M:%SZ")
#
#     for i, eem_type in enumerate(enum_energy_efficiency_measurement_type):
#         df[f"eem_{i}_subject"] = df['subject'].apply(lambda x: f"{x}-{eem_type}").apply(eem_subject)
#     for saving_type in enum_energy_saving_type:
#         df[f'project_energy_saving_subject_{saving_type}'] = df['subject'] \
#             .apply(lambda x: f"{x}-project-{saving_type}").apply(energy_saving_subject)
#     return df[['subject', 'project_subject', 'epc_date_before', 'epc_date'] +
#               [x for x in df.columns if re.match("eem_.*_subject", x)] +
#               [x for x in df.columns if re.match("total_.*", x)] +
#               [x for x in df.columns if re.match("energy_saving_.*_subject", x)] +
#               [x for x in df.columns if re.match("project_energy_saving_subject_.*", x)]]


# def harmonize_ts(data, **kwargs):
#     namespace = kwargs['namespace']
#     user = kwargs['user']
#     n = Namespace(namespace)
#     config = kwargs['config']
#     freq = 'PT1Y'
#
#     df = pd.DataFrame.from_records(data)
#
#     neo4j_connection = config['neo4j']
#
#     measured_property_list = ['EnergyConsumptionOil', 'EnergyConsumptionCoal',
#                               'EnergyConsumptionGas', 'EnergyConsumptionOthers',
#                               'EnergyConsumptionDistrictHeating',
#                               'EnergyConsumptionGridElectricity', 'EnergyConsumptionTotal']
#
#     measured_property_df = ['annual_energy_consumption_before_liquid_fuels',
#                             'annual_energy_consumption_before_hard_fuels',
#                             'annual_energy_consumption_before_gas', 'annual_energy_consumption_before_others',
#                             'annual_energy_consumption_before_heat_energy',
#                             'annual_energy_consumption_before_electricity',
#                             'annual_energy_consumption_before_total_consumption']
#
#     neo = GraphDatabase.driver(**neo4j_connection)
#     hbase_conn2 = config['hbase_store_harmonized_data']
#
#     with neo.session() as session:
#         for i in range(len(measured_property_list)):
#             print(measured_property_list[i])
#             for index, row in df.iterrows():
#                 device_uri = str(n[row['device_subject']])
#
#                 sensor_id = sensor_subject(config['source'], row['subject'], measured_property_list[i], "RAW",
#                                            freq)
#                 sensor_uri = str(n[sensor_id])
#                 measurement_id = hashlib.sha256(sensor_uri.encode("utf-8"))
#                 measurement_id = measurement_id.hexdigest()
#                 measurement_uri = str(n[measurement_id])
#
#                 create_sensor(session=session, device_uri=device_uri, sensor_uri=sensor_uri, unit_uri=units["KiloW-HR"],
#                               property_uri=bigg_enums[measured_property_list[i]],
#                               estimation_method_uri=bigg_enums.Naive,
#                               measurement_uri=measurement_uri, is_regular=True,
#                               is_cumulative=False, is_on_change=False, freq=freq, agg_func="SUM",
#                               dt_ini=pd.Timestamp(row['epc_date_before']),
#                               dt_end=pd.Timestamp(row['epc_date']), ns_mappings=settings.namespace_mappings)
#             reduced_df = df[[measured_property_df[i]]]
#
#             reduced_df['listKey'] = measurement_id
#             reduced_df['isReal'] = False
#             reduced_df['bucket'] = ((pd.to_datetime(df['epc_date_before']).values.astype(
#                 int) // 10 ** 9) // settings.ts_buckets) % settings.buckets
#             reduced_df['start'] = (pd.to_datetime(df['epc_date_before']).values.astype(int)) // 10 ** 9
#             reduced_df['end'] = (pd.to_datetime(df['epc_date']).values.astype(int)) // 10 ** 9
#
#             reduced_df.rename(
#                 columns={measured_property_df[i]: "value"},
#                 inplace=True)
#
#             device_table = f"harmonized_online_{measured_property_list[i]}_100_SUM_{freq}_{user}"
#
#             save_to_hbase(reduced_df.to_dict(orient="records"), device_table, hbase_conn2,
#                           [("info", ['end', 'isReal']), ("v", ['value'])],
#                           row_fields=['bucket', 'listKey', 'start'])
#
#             period_table = f"harmonized_batch_{measured_property_list[i]}_100_SUM_{freq}_{user}"
#
#             save_to_hbase(reduced_df.to_dict(orient="records"), period_table, hbase_conn2,
#                           [("info", ['end', 'isReal']), ("v", ['value'])],
#                           row_fields=['bucket', 'start', 'listKey'])
#         print("finished")
#
#     # save_rdf_with_source(g, config['source'], config['neo4j'])
#     # link_devices_with_source(df_building, n, config['neo4j'])
#     #
#     # parts_eem = 2
#     # parts_saving = 2
#     # start_column_eem = 0
#     # for chunk in range(parts_eem):
#     #     k, m = divmod(len(enum_energy_efficiency_measurement_type), parts_eem)
#     #     eems_parted = [enum_energy_efficiency_measurement_type[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in
#     #                    range(parts_eem)]
#     #     df_eem = clean_dataframe_eem_savings(df.copy(), eems_parted[chunk], start_column_eem)
#     #     start_column_saving = 0
#     #     for chunk_saving in range(parts_saving):
#     #         k, m = divmod(len(enum_energy_saving_type), parts_saving)
#     #         saving_parted = [enum_energy_saving_type[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in
#     #                          range(parts_saving)]
#     #         mapper.select_chunk(eems_parted[chunk], start_column_eem, saving_parted[chunk_saving], start_column_saving)
#     #         g = generate_rdf(mapper.get_mappings("eem_savings"), df_eem)
#     #         try:
#     #             save_rdf_with_source(g, config['source'], config['neo4j'])
#     #         except Exception:
#     #             g.serialize("error.ttl")
#     #             raise Exception("File in error.ttl")
#     #         start_column_saving += len(saving_parted[chunk_saving])
#     #     start_column_eem += len(eems_parted[chunk])
#     #
#     # df_project = clean_dataframe_project(df.copy())
#     # g = generate_rdf(mapper.get_mappings("project_info"), df_project)
#     # save_rdf_with_source(g, config['source'], config['neo4j'])
#     # harmonize_ts(df_building.to_dict(orient="records"), namespace=namespace, user=user, config=config)
