"""
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

#Weather station
"""
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

#REPAIR SPLIT measurementLists
"""

#
ADD a new_created=0 param to all

Match(n:ns0__MeasurementList) set n.new_created = 0 return n

# create a merged node

Match(d:ns0__Device)-[:ns0__hasMeasurementLists]->(n:ns0__MeasurementList) 
WITH d, n.uri AS uri, n.ns0__measurementKey AS key1, n.ns0__measurementListEnd as endsss,
 n.ns0__measurementListStart as startsss, n.ns0__measuredProperty as ns0__measuredProperty, n.ns0__measurementFrequency as ns0__measurementFrequency, n.ns0__measurementUnit as ns0__measurementUnit
WITH d, uri, key1, apoc.agg.maxItems(key1,endsss) as maxDate, apoc.agg.minItems(key1,startsss) as minDate, ns0__measuredProperty, ns0__measurementFrequency, ns0__measurementUnit
CREATE(n2:ns0__MeasurementList{uri: uri, ns0__measurementKey: key1, ns0__measurementListEnd: maxDate.value, ns0__measurementListStart: minDate.value,
 ns0__measuredProperty: ns0__measuredProperty, ns0__measurementFrequency: ns0__measurementFrequency, ns0__measurementUnit: ns0__measurementUnit, new_created: 1})
Merge (d)-[:ns0__hasMeasurementLists]->(n2)
RETURN d, n2

# remove all non new created lists

Match(n:ns0__MeasurementList{new_created:0}) detach delete n

# remove the filter field
Match (n:ns0__MeasurementList) REMOVE n.new_created return n


"""