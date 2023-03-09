import argparse
import os
from neo4j import GraphDatabase
import settings
import set_up_params
from utils import utils
from ontology.namespaces_definition import *
from utils.rdf.rdf_functions import get_namespace_subject

bigg = settings.namespace_mappings['bigg']


def create_dev_agg(measured_property, device_query, freq, agg_name, required, agg_func):
    id_prop = get_namespace_subject(measured_property)[1]
    return f"""
    CALL{{
        MATCH(prop {{uri:"{measured_property}"}}) 
        RETURN prop
    }}
    MATCH (bs:{bigg}__BuildingSpace)-[:{bigg}__isObservedByDevice]->(d)-
        [:{bigg}__hasSensor]->(s:{bigg}__Sensor)-[:{bigg}__hasMeasurement]->(ts:{bigg}__Measurement) 
    WHERE {device_query} 
          AND s.{bigg}__timeSeriesFrequency="{freq}" 
          AND EXISTS((s)-[:{bigg}__hasMeasuredProperty]->(prop))
    WITH bs, d, prop, ts, bs.uri + "-AGGREGATOR-{id_prop}-{agg_name}" as uri
    MERGE (da:{bigg}__DeviceAggregator:Resource{{uri:uri}})
    MERGE (da)-[:{bigg}__includesDevice]->(d)
    WITH da, apoc.text.join(collect("<mi>"+split(ts.uri,"#")[1]+"</mi>"), "<mo>"+"+"+"</mo>") as key1, prop, bs
    SET da.required = {required}, 
        da.{bigg}__deviceAggregatorName = "{agg_name}",
        da.{bigg}__deviceAggregatorFrequency = "{freq}",
        da.{bigg}__deviceAggregatorFormula=key1,
        da.{bigg}__deviceAggregatorTimeAggregationFunction = {agg_func}
    MERGE (da)-[:{bigg}__hasDeviceAggregatorProperty]->(prop)
    MERGE (bs)-[:{bigg}__hasDeviceAggregator]->(da)    
    RETURN da
    """


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='setup of devices aggregators')
    parser.add_argument("--device_aggregator_type", "-type", help="The type of device aggregator", required=True)
    parser.add_argument("--country", "-cn", help="The country to generate device aggregators", required=True)
    if os.getenv("PYCHARM_HOSTED"):
        args_t = ["-type", "totalGasConsumption"]
        args = parser.parse_args(args_t)
    else:
        args = parser.parse_args()
    # read config file
    config = utils.read_config(settings.conf_file)
    neo4j = GraphDatabase.driver(**config['neo4j'])
    d_agg = set_up_params.DEVICE_AGGREGATORS[args.country]
    for query_params in d_agg[args.device_aggregator_type]:
        query = create_dev_agg(**query_params)
        print(query)
        with neo4j.session() as session:
            session.run(query)
