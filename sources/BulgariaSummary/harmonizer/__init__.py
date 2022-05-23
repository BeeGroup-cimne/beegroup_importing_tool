from datetime import timedelta

import pandas as pd
import rdflib
from rdflib import Namespace
from thefuzz import process

from sources.BulgariaSummary.harmonizer.Mapper import Mapper
from utils.rdf_utils.rdf_functions import generate_rdf

energy_type_list = ['OilSaving', 'CoalSaving', 'GasSaving', 'OtherSavings', 'DistrictHeatingSaving',
                    'GridElectricitySaving',
                    'TotalEnergySaving']

energy_efficiency_measurement_list = ['BuildingFabricMeasure.WallMeasure.WallCavityInsulation',
                                      'BuildingFabricMeasure.WallMeasure.WallInternalInsulation',
                                      'BuildingFabricMeasure.RoofAndCeilingMeasure',
                                      'BuildingFabricMeasure.FloorMeasure', 'BuildingFabricMeasure',
                                      'HVACAndHotWaterMeasure',
                                      'HVACAndHotWaterMeasure.CombinedHeatingCoolingSystemMeasure',
                                      'HVACAndHotWaterMeasure.HeatingSystemMeasure.HeatingFinalElementsMeasure.HeatingFinalElementsReplacement',
                                      'HVACAndHotWaterMeasure.CombinedHeatingCoolingSystemMeasure.HeatingAndCoolingDistributionMeasure.HeatingAndCoolingDistributionSystemReplacement',
                                      'HVACAndHotWaterMeasure.CombinedHeatingCoolingSystemMeasure.HeatingAndCoolingControlMeasure',
                                      'HVACAndHotWaterMeasure.HotWaterSystemMeasure.HotWaterProductionMeasure.OtherHotWaterProductionMeasure',
                                      'RenewableGenerationMeasure',
                                      'LightingMeasure',
                                      'ElectricPowerSystemMeasure.ElectricEquipmentMeasure.ElectricApplianceMeasure'
                                      ]


def harmonize_command_line():
    pass


def set_taxonomy(df):
    df['type_of_building'] = df['type_of_building'].str.strip()
    tax_df = pd.read_excel("data/tax/TAX_BULGARIA.xlsx", header=None, names=["Source", "Taxonomy"], sheet_name='Hoja1')
    tax_dict = {}
    for i in tax_df.to_dict(orient="records"):
        tax_dict.update({i['Source']: i['Taxonomy']})

    df['type_of_building'] = df['type_of_building'].map(tax_dict)
    return df


def set_country(df, label='municipality', predicates=None,
                dictionary_ttl_file="utils/rdf_utils/ontology/dictionaries/municipality.ttl"):
    if predicates is None:
        predicates = ['ns1:name']

    unique_municipalities = list(df[label].unique())

    dicty = rdflib.Graph()
    dicty.load(dictionary_ttl_file, format="ttl")
    query = f"""SELECT ?s ?obj WHERE{{ {" UNION ".join([f"{{ ?s {p} ?obj }}" for p in predicates])} }}"""
    obj = dicty.query(query)
    map_dict = {o[1]: o[0] for o in obj}

    mapping_dict = {}
    for i in unique_municipalities:
        match, score = process.extractOne(i, list(map_dict.keys()), score_cutoff=90)
        mapping_dict.update({i: map_dict[match]})

    df['municipality'] = df['municipality'].map(mapping_dict)
    return df


def harmonize_data(data, **kwargs):
    namespace = kwargs['namespace']
    user = kwargs['user']
    n = Namespace(namespace)
    config = kwargs['config']

    df = set_taxonomy(pd.DataFrame().from_records(data))

    df['subject'] = df['filename'] + '-' + df['id'].astype(str)

    df['organization_subject'] = 'ORGANIZATION-' + df['subject']

    df['building_subject'] = 'BUILDING-' + df['subject']
    df['building_name'] = df['subject'] + '-' + df['municipality'] + '-' + df['type_of_building']

    df['location_subject'] = 'LOCATION-' + df['subject']

    df['epc_date_before'] = df['epc_date'] - timedelta(days=365)
    df['epc_subject_before'] = 'EPC-' + df['subject'] + '-' + df['epc_energy_class_before']
    df['epc_subject_after'] = 'EPC-' + df['subject'] + '-' + df['epc_energy_class_after']

    df['building_space_subject'] = 'BUILDINGSPACE-' + df['subject']
    df['building_space_use_type_subject'] = 'BUILDING-SPACE-USE-TYPE-' + df['subject']

    df['gross_floor_area_subject'] = 'AREA-GrossFloorArea-' + config['source'] + '-' + df['subject']
    df['element_subject'] = 'ELEMENT-' + df['subject']

    df['device_subject'] = 'DEVICE-' + config['source'] + '-' + df['subject']

    value_dict = {0: 'OilSaving', 1: 'CoalSaving', 2: 'GasSaving',
                  3: 'OtherSavings', 4: 'DistrictHeatingSaving',
                  5: 'GridElectricitySaving',
                  6: 'TotalEnergySaving'}

    for i in range(len(energy_efficiency_measurement_list)):
        df[f"subject_eem_{i}"] = 'EEM-' + df['subject'] + '-' + energy_efficiency_measurement_list[i]
        df[f"emm_{i}_type"] = energy_efficiency_measurement_list[i]
        for j in range(7):
            df[f"energy_saving_{i}_{j}_subject"] = 'EnergySaving-' + df['subject'] + '-' + \
                                                   energy_efficiency_measurement_list[
                                                       i] + '-' + value_dict[j]
            df[f"energy_saving_{i}_{j}_type"] = value_dict[j]

    df.dropna(subset=['epc_subject_before'], inplace=True)

    mapper = Mapper(config['source'], n)
    g = generate_rdf(mapper.get_mappings("all"), df)

    print(g.serialize(format="ttl"))

    with open('out.ttl', 'w') as f:
        f.write(g.serialize(format="ttl"))

# save_rdf_with_source(g, config['source'], config['neo4j'])
# create_sensor
