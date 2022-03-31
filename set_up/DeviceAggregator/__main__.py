import argparse
import os
from neo4j import GraphDatabase
import settings
from utils import utils

total_electricity_device_agg = """
Match (bs:ns0__BuildingSpace)-[:ns0__isObservedBy]->(d:ns0__Device{ns0__source:"datadis"})-[:ns0__hasMeasurementLists]->(ml:ns0__MeasurementList)
where ml.ns0__measurementFrequency="1h"
with bs as bs, apoc.text.join(collect("<mi>"+ml.ns0__measurementKey+"</mi>"), "<mo>"+"+"+"</mo>") as key1, split(bs.uri, "-")[0]+"-AGGREGATOR-ELECTRICITY-TOTAL-"+split(bs.uri, "-")[1] as uri
Merge (da:ns0__DeviceAggregator{uri:uri, ns0__measuredProperty: "electricityConsumption",
    ns0__required: "true", ns0__deviceAggregatorName: "totalElectricityConsumption",
    ns0__deviceAggregatorFrequency: "1h",
    ns0__formula: key1}
    )
Merge (bs)-[:ns0__hasDeviceAggregator]->(da)
With bs as bs, da as da
Match (bs:ns0__BuildingSpace)-[:ns0__isObservedBy]->(d:ns0__Device{ns0__source:"datadis"})
Merge (da)-[:ns0__includesDevice]->(d)
Return da

"""

outdoor_weather_device_agg = """
Match (bs:ns0__BuildingSpace)-[:ns0__isObservedBy]->(d:ns0__Device:ns0__WeatherStation)-[:ns0__hasMeasurementLists]->(ml:ns0__MeasurementList)
where ml.ns0__measurementFrequency="1h"
with bs as bs, apoc.text.join(collect("<mi>"+ml.ns0__measurementKey+"</mi>"), "<mo>"+"+"+"</mo>") as key1, split(bs.uri, "-")[0]+"-AGGREGATOR-METEO-TOTAL-"+split(bs.uri, "-")[1] as uri
Merge (da:ns0__DeviceAggregator{uri:uri, ns0__measuredProperty: "meteo",
    ns0__required: "true", ns0__deviceAggregatorName: "externalWeather",
    ns0__deviceAggregatorFrequency: "1h",
    ns0__formula: key1}
    )
Merge (bs)-[:ns0__hasDeviceAggregator]->(da)
With bs as bs, da as da
Match (bs:ns0__BuildingSpace)-[:ns0__isObservedBy]->(d:ns0__Device:ns0__WeatherStation)
Merge (da)-[:ns0__includesDevice]->(d)
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

