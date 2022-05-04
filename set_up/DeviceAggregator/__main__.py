import argparse
import os
from neo4j import GraphDatabase
import settings
from utils import utils

bigg = settings.namespace_mappings['bigg']

total_electricity_device_agg = f"""
MATCH(prop {{uri:"http://bigg-project.eu/ontology#EnergyConsumptionGridElectricity"}})
WITH prop
CALL{{
    MATCH (bs:{bigg}__BuildingSpace)-[:{bigg}__isObservedByDevice]->(d:{bigg}__Device{{source:"DatadisSource"}})-
    [:{bigg}__hasSensor]->(s:{bigg}__Sensor)-[:{bigg}__hasMeasurement]->(ts:{bigg}__Measurement)
    WHERE s.{bigg}__sensorFrequency="PT1H" 
    WITH bs, d, apoc.text.join(collect("<mi>"+split(ts.uri,"#")[1]+"</mi>"), "<mo>"+"+"+"</mo>") as key1, split(bs.uri, "-")[0]+"-AGGREGATOR-ELECTRICITY-TOTAL-"+split(bs.uri, "-")[1] as uri
    RETURN uri, key1, bs, d}}
MERGE (da:{bigg}__DeviceAggregator{{uri:uri}})-[:{bigg}__hasMeasuredProperty]->(prop)
SET da.required = true, 
    da.{bigg}__deviceAggregatorName = "totalElectricityConsumption",
    da.{bigg}__deviceAggregatorFrequency = "PT1H",
    da.{bigg}__deviceAggregatorFormula= key1
MERGE (bs)-[:{bigg}__hasDeviceAggregator]->(da)
WITH da as da, d as d
MERGE (da)-[:{bigg}__includesDevice]->(d)
RETURN da
"""


outdoor_weather_device_agg = f"""
Match (bs:{bigg}__BuildingSpace)-[:{bigg}____isObservedByDevice]->(d:{bigg}__Device:{bigg}__WeatherStation)-
[:{bigg}__hasSensor]->(s:{bigg}__Sensor)-[:{bigg}__hasMeasurement]->(ts:{bigg}__Measurement)
WHERE s.{bigg}__sensorFrequency="PT1H" 
WITH bs as bs, d as d, apoc.text.join(collect("<mi>"+split(ts.uri,"#")[1]+"</mi>"), "<mo>"+"+"+"</mo>") as key1, split(bs.uri, "-")[0]+"-AGGREGATOR-METEO-TOTAL-"+split(bs.uri, "-")[1] as uri
Match(prop {{uri:"http://bigg-project.eu/ontology#EnergyConsumptionGridElectricity"}})
Merge (da:{bigg}__DeviceAggregator{{uri:uri}})-[:{bigg}__hasMeasuredProperty]->(prop)
SET da.required = true,
    da.{bigg}__deviceAggregatorName: "externalWeather",
    da.{bigg}__deviceAggregatorFrequency: "PT1H",
    da.{bigg}__deviceAggregatorFormula: key1
Merge (bs)-[:{bigg}__hasDeviceAggregator]->(da)
With bs as bs, d as d
Merge (da)-[:{bigg}__includesDevice]->(d)
Return da
"""

d_agg = {
    "totalElectricityConsumption": total_electricity_device_agg,
    "externalWeather": outdoor_weather_device_agg
}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='setup of devices aggregators')
    parser.add_argument("--device_aggregator_type", "-type", help="The type of device aggregator", required=True)
    if os.getenv("PYCHARM_HOSTED"):
        args_t = ["-type", "totalElectricityConsumption"]
        args = parser.parse_args(args_t)
    else:
        args = parser.parse_args()
    # read config file
    config = utils.read_config(settings.conf_file)
    neo4j = GraphDatabase.driver(**config['neo4j'])
    with neo4j.session() as session:
        session.run(d_agg[args.device_aggregator_type])

