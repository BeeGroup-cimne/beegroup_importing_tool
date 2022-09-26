import pandas as pd
from neo4j import GraphDatabase
from rdflib import Namespace

from harmonizer.cache import Cache
from sources.OpenData.harmonizer.mapper import Mapper
from utils.data_transformations import location_info_subject, fuzz_location, cadastral_info_subject, \
    building_subject, additional_epc_subject, epc_subject
from utils.rdf_utils.rdf_functions import generate_rdf
from utils.rdf_utils.save_rdf import save_rdf_with_source


def clean_data(data, n, neo):
    _df = pd.DataFrame(data)

    # Building
    with neo.session() as session:
        res = session.run(
            f"""MATCH (b:bigg__Building)-[:bigg__hasCadastralInfo]-(c:bigg__CadastralInfo),
            (b:bigg__Building)<-[:bigg__managesBuilding|bigg__hasSubOrganization *]-(o:bigg__Organization{{userID:'icaen'}}) 
             RETURN b.bigg__buildingIDFromOrganization as building_id, c.bigg__landCadastralReference as cadastral_ref """).data()

    building_df = pd.DataFrame(res)

    df = pd.merge(left=building_df, right=_df, left_on='cadastral_ref',
                  right_on='referencia_cadastral')
    # [{'building_id': '02058', 'cadastral_ref': '08016A011000200000TH', 'num_cas': '5CQWHG9LX', 'adre_a': 'Carretera DEL PARC (CENTRE PISCÍCOLA)', 'numero': 'S/N', 'codi_postal': '08695', 'poblacio': 'Bagà', 'comarca': 'Berguedà', 'nom_provincia': 'Barcelona', 'codi_poblacio': '08016', 'codi_comarca': '14', 'codi_provincia': '08', 'referencia_cadastral': '08016A011000200000TH', 'zona_climatica': 'E1', 'metres_cadastre': '514', 'us_edifici': 'Terciari', 'qualificaci_de_consum_d': 'A', 'energia_prim_ria_no_renovable': '33.61', 'qualificacio_d_emissions': 'A', 'emissions_de_co2': '7.27', 'vehicle_electric': 'NO', 'solar_termica': 'NO', 'solar_fotovoltaica': 'NO', 'sistema_biomassa': 'SI', 'xarxa_districte': 'NO', 'energia_geotermica': 'NO', 'eina_de_certificacio': 'CE3X', 'motiu_de_la_certificacio': 'Edifici existent de l’administració pública', 'valor_aillaments_cte': '0.55', 'valor_finestres_cte': '2.5', 'normativa_construcci': 'NRE-AT-87', 'tipus_tramit': 'Edificis existents', 'data_entrada': '2022-07-06T00:00:00.000', 'rehabilitacio_energetica': 'NO', 'actuacions_rehabilitacio': nan, 'escala': nan, 'pis': nan, 'porta': nan, 'consum_d_energia_final': '143.43', 'cost_anual_aproximat_d_energia': '5.56', 'valor_aillaments': '2.38', 'valor_finestres': '3.54', 'tipus_terciari': 'Altres', 'ventilacio_us_residencial': nan}]
    if not df.empty:
        # print(df.to_dict(orient='records'))

        df['building_subject'] = df['building_id'].apply(building_subject)
        df['building_uri'] = df['building_subject'].apply(lambda x: n[x])

        # Location
        df['location_subject'] = df['building_id'].apply(location_info_subject)
        df['location_uri'] = df['location_subject'].apply(lambda x: n[x])

        df['hasAddressCity'] = df['poblacio'].map(
            fuzz_location(Cache.municipality_dic_ES, ['ns1:name'], df['poblacio'].unique()))

        df['hasAddressProvince'] = df['nom_provincia'].map(
            fuzz_location(Cache.province_dic_ES, ['ns1:name', 'ns1:officialName'],
                          df['nom_provincia'].dropna().unique()))

        # Cadastral Reference
        df['cadastral_subject'] = df['referencia_cadastral'].apply(cadastral_info_subject)
        df['cadastral_uri'] = df['cadastral_subject'].apply(lambda x: n[x])

        # EPC
        df['epc_subject'] = df['num_cas'].apply(epc_subject)

        df['epc_uri'] = df['epc_subject'].apply(lambda x: n[x])

        # EPC Additional Info
        df['additional_epc_subject'] = df['num_cas'].apply(additional_epc_subject)
        df['additional_epc_uri'] = df['additional_epc_subject'].apply(lambda x: n[x])

    return df


def harmonize_data(data, **kwargs):
    # import utils.utils
    # config = utils.utils.read_config('config.json')
    # config.update({"source": 'opendata'})
    # namespace = "https://opendata.cat#"

    namespace = kwargs['namespace']
    config = kwargs['config']
    n = Namespace(namespace)

    neo4j_connection = config['neo4j']
    neo = GraphDatabase.driver(**neo4j_connection)

    df = clean_data(data, n, neo)

    if not df.empty:
        mapper = Mapper(config['source'], n)
        g = generate_rdf(mapper.get_mappings("all"), df)

        g.serialize('output.ttl', format="ttl")

        save_rdf_with_source(g, config['source'], config['neo4j'])
