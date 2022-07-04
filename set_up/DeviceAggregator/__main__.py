import argparse
import os
from neo4j import GraphDatabase
import settings
from utils import utils
from utils.rdf_utils.ontology.namespaces_definition import bigg_enums
from utils.rdf_utils.ontology.generate_namespaces import get_namespace_subject

bigg = settings.namespace_mappings['bigg']


def create_dev_agg(measured_property, device_query, freq, agg_name, required, agg_func):
    id_prop = get_namespace_subject(measured_property)[1]
    return f"""
    CALL{{
        MATCH(prop {{uri:"{measured_property}"}}) 
        RETURN prop
    }}
    MATCH (bs:{bigg}__BuildingSpace)-[:{bigg}__isObservedByDevice]->(d:{device_query})-
        [:{bigg}__hasSensor]->(s:{bigg}__Sensor)-[:{bigg}__hasMeasurement]->(ts:{bigg}__Measurement) 
    WHERE s.{bigg}__timeSeriesFrequency=["{freq}"] 
          AND EXISTS((s)-[:{bigg}__hasMeasuredProperty]->(prop))
    WITH bs, d, prop, ts, split(bs.uri, "-")[0]+"-AGGREGATOR-{id_prop}-TOTAL-"+split(bs.uri, "-")[1] as uri
    MERGE (da:{bigg}__DeviceAggregator:Resource{{uri:uri}})
    MERGE (da)-[:{bigg}__includesDevice]->(d)
    WITH da, apoc.text.join(collect("<mi>"+split(ts.uri,"#")[1]+"</mi>"), "<mo>"+"+"+"</mo>") as key1, prop, bs
    SET da.required = [{required}], 
        da.{bigg}__deviceAggregatorName = ["{agg_name}"],
        da.{bigg}__deviceAggregatorFrequency = ["{freq}"],
        da.{bigg}__deviceAggregatorFormula=[key1],
        da.{bigg}__deviceAggregatorTimeAggregationFunction=["{agg_func}"]
    MERGE (da)-[:{bigg}__hasDeviceAggregatorProperty]->(prop)
    MERGE (bs)-[:{bigg}__hasDeviceAggregator]->(da)    
    RETURN da
    """


total_electricity_device_agg = [
    create_dev_agg(
        measured_property=bigg_enums.EnergyConsumptionGridElectricity,
        device_query=f"""{bigg}__Device{{source:"DatadisSource"}}""",
        freq="PT1H",
        agg_name="totalElectricityConsumption",
        required="true",
        agg_func="SUM"
    )
]

total_gas_device_agg = [
    create_dev_agg(
        measured_property=bigg_enums.EnergyConsumptionGas,
        device_query=f"""{bigg}__Device{{source:"NedgiaSource"}}""",
        freq="",
        agg_name="totalGasConsumption",
        required="true",
        agg_func="SUM"
    )
]

outdoor_weather_device_agg = [
    create_dev_agg(
        measured_property=bigg_enums.Temperature,
        device_query=f"""{bigg}__Device:{bigg}__WeatherStation""",
        freq="PT1H",
        agg_name="outdoorTemperature",
        required="true",
        agg_func="AVG"
    ),
    create_dev_agg(
        measured_property=bigg_enums.HumidityRatio,
        device_query=f"""{bigg}__Device:{bigg}__WeatherStation""",
        freq="PT1H",
        agg_name="outdoorHumidityRatio",
        required="false",
        agg_func="AVG"
    )
]


d_agg = {
    "totalGasConsumption": total_gas_device_agg,
    "totalElectricityConsumption": total_electricity_device_agg,
    "externalWeather": outdoor_weather_device_agg
}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='setup of devices aggregators')
    parser.add_argument("--device_aggregator_type", "-type", help="The type of device aggregator", required=True)
    if os.getenv("PYCHARM_HOSTED"):
        args_t = ["-type", "totalGasConsumption"]
        args = parser.parse_args(args_t)
    else:
        args = parser.parse_args()
    # read config file
    config = utils.read_config(settings.conf_file)
    neo4j = GraphDatabase.driver(**config['neo4j'])
    for query in d_agg[args.device_aggregator_type]:
        with neo4j.session() as session:
            session.run(query)

