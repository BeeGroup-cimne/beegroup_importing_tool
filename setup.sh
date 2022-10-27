 # RUN in new neo4j
 CREATE CONSTRAINT n10s_unique_uri ON (r:Resource) ASSERT r.uri IS UNIQUE
 # Create the tags and namesapaces
 CALL n10s.graphconfig.init({ keepLangTag: true, handleMultival:"ARRAY"});
 CALL n10s.nsprefixes.add("bigg","http://bigg-project.eu/ontology#");
 CALL n10s.nsprefixes.add("geo","http://www.geonames.org/ontology#");
 CALL n10s.nsprefixes.add("unit","http://qudt.org/vocab/unit/");
 CALL n10s.nsprefixes.add("wgs","http://www.w3.org/2003/01/geo/wgs84_pos#");
 ###CALL n10s.nsprefixes.add("ttt","http://ttt.cat#");

## TEST
CALL n10s.graphconfig.init({ keepLangTag: true, handleMultival:"ARRAY", multivalPropList:["http://www.w3.org/2000/01/rdf-schema#label", "http://www.w3.org/2000/01/rdf-schema#comment", "http://www.geonames.org/ontology#officialName"]});
 CALL n10s.nsprefixes.add("bigg","http://bigg-project.eu/ontology#");
 CALL n10s.nsprefixes.add("geo","http://www.geonames.org/ontology#");
 CALL n10s.nsprefixes.add("unit","http://qudt.org/vocab/unit/");
 CALL n10s.nsprefixes.add("wgs","http://www.w3.org/2003/01/geo/wgs84_pos#");

# Create the dictionary of elements
echo "dict"
python3 -m set_up.Dictionaries

# add translation labels
python3 -m utils.rdf_utils.ontology.taxonomy_translations  translate

### General Setup
echo "weather stations"
python3 -m set_up.Weather -f data/Weather/cpcat.json -n "https://weather.beegroup-cimne.com#" -c

### ICAEN ORGANIZATION "https://icaen.cat#"
# SET UP
echo "org"
python3 -m set_up.Organizations -f data/Organizations/gencat-organizations.xls -name "Generalitat de Catalunya" -u "icaen" -n "https://icaen.cat#"
echo "Gemweb source"
python3 -m set_up.DataSources -u "icaen" -n "https://icaen.cat#" -f data/DataSources/gemweb.xls -d GemwebSource
echo "datadis source"
python3 -m set_up.DataSources -u "icaen" -n "https://icaen.cat#" -f data/DataSources/datadis.xls -d DatadisSource
echo "nedgia source"
python3 -m set_up.DataSources -u "icaen" -n "https://icaen.cat#" -f data/DataSources/nedgia.xls -d NedgiaSource
echo "simpleTariff source"
python3 -m set_up.DataSources -u "icaen" -n "https://icaen.cat#" -f data/DataSources/simpleTariff.xls -d SimpleTariffSource
# create a new Tariff for this source and organization
"""
Match (o:bigg__Organization{userID:"icaen"})
Match (s:SimpleTariffSource) where (s)<-[:hasSource]-(o)
Merge (t:bigg__Tariff{bigg__tariffCompany:"CIMNE", bigg__tariffName: "electricdefault", uri: "https://icaen.cat#TARIFF-SimpleTariffSource-icaen-electricdefault"})-[:importedFromSource]->(s)
return t;
Match (o:bigg__Organization{userID:"icaen"})
Match (s:SimpleTariffSource) where (s)<-[:hasSource]-(o)
Merge (t:bigg__Tariff{bigg__tariffCompany:"CIMNE", bigg__tariffName: "gasdefault", uri: "https://icaen.cat#TARIFF-SimpleTariffSource-icaen-gasdefault"})-[:importedFromSource]->(s)
return t;
"""
#
# link all buildings to tariff
"""
Match (bigg__Organization{userID:"icaen"})-[:hasSource]->(:SimpleTariffSource)<-[:importedFromSource]-(t:bigg__Tariff{bigg__tariffName:"electricdefault"})
Match (dt {uri:"http://bigg-project.eu/ontology#Electricity"})
Match (bigg__Organization{userID:"icaen"})-[:bigg__hasSubOrganization*]->()-[:bigg__managesBuilding]->()-[:bigg__hasSpace]->()-[:bigg__hasUtilityPointOfDelivery]->(s)-[:bigg__hasUtilityType]->(dt)
Merge (c:bigg__ContractedTariff:Resource{bigg__contractStartDate: datetime("2000-01-01T00:00:00.000+0100"), bigg__contractName:"electricdefault", uri: s.uri+"_tariff"})
Merge (s)-[:bigg__hasContractedTariff]->(c)
Merge (c)-[:bigg__hastariff]->(t)
return t;
Match (bigg__Organization{userID:"icaen"})-[:hasSource]->(:SimpleTariffSource)<-[:importedFromSource]-(t:bigg__Tariff{bigg__tariffName:"gasdefault"})
Match (dt {uri:"http://bigg-project.eu/ontology#Gas"})
Match (bigg__Organization{userID:"icaen"})-[:bigg__hasSubOrganization*]->()-[:bigg__managesBuilding]->()-[:bigg__hasSpace]->()-[:bigg__hasUtilityPointOfDelivery]->(s)-[:bigg__hasUtilityType]->(dt)
Merge (c:bigg__ContractedTariff:Resource{bigg__contractStartDate: datetime("2000-01-01T00:00:00.000+0100"), bigg__contractName:"gasdefault", uri: s.uri+"_tariff"})
Merge (s)-[:bigg__hasContractedTariff]->(c)
Merge (c)-[:bigg__hastariff]->(t)
return t;
"""
# create general Emissions node.
"""
Merge (t:bigg__CO2EmissionsFactor:Resource{bigg__CO2EmissionsStation:"cataloniaElectric", wgs__lon:40.959, wgs__lat:1.485, uri: "https://weather.beegroup-cimne.com#CO2EMISIONS-cataloniaElectric"})
return t;
Merge (t:bigg__CO2EmissionsFactor:Resource{bigg__CO2EmissionsStation:"cataloniaGas", wgs__lon:40.959, wgs__lat:1.485, uri: "https://weather.beegroup-cimne.com#CO2EMISIONS-cataloniaGas"})
return t;
"""

# link all supplies to CO2Emissions
"""
Match (co2:bigg__CO2EmissionsFactor{bigg__CO2EmissionsStation:"cataloniaElectric"})
Match (dt {uri:"http://bigg-project.eu/ontology#Electricity"})
Match (bigg__Organization{userID:"icaen"})-[:bigg__hasSubOrganization*]->()-[:bigg__managesBuilding]->()-[:bigg__hasSpace]->()-[:bigg__hasUtilityPointOfDelivery]->(s)-[:bigg__hasUtilityType]->(dt)
Merge (s)-[:bigg__hasCO2EmissionsFactor]->(co2)
return co2;
Match (co2:bigg__CO2EmissionsFactor{bigg__CO2EmissionsStation:"cataloniaGas"})
Match (dt {uri:"http://bigg-project.eu/ontology#Gas"})
Match (bigg__Organization{userID:"icaen"})-[:bigg__hasSubOrganization*]->()-[:bigg__managesBuilding]->()-[:bigg__hasSpace]->()-[:bigg__hasUtilityPointOfDelivery]->(s)-[:bigg__hasUtilityType]->(dt)
Merge (s)-[:bigg__hasCO2EmissionsFactor]->(co2)
return co2;
"""

# LOAD DATA HBASE
echo "GPG"
python3 -m harmonizer -so GPG -u "icaen" -n "https://icaen.cat#" -o -c
echo "Gemweb"
python3 -m harmonizer -so Gemweb -u "icaen" -n "https://icaen.cat#" -c
echo "Genercat"
python3 -m harmonizer -so Genercat -u "icaen" -n "https://icaen.cat#" -c
echo "Datadis static"
python3 -m harmonizer -so Datadis -n "https://icaen.cat#" -u icaen -t static -c
python3 -m harmonizer -so CEEC3X -n "https://icaen.cat#" -u icaen -c

-
echo "Link WS with Buildings"
python3 -m set_up.Weather -f data/Weather/cpcat.json -n "https://weather.beegroup-cimne.com#" -u


# load TS
echo "Datadis TS"
python3 -m harmonizer -so Datadis -n "https://icaen.cat#" -u icaen -t fast-ts -c
echo "Nedgia"
python3 -m harmonizer -so Nedgia -n "https://icaen.cat#" -u icaen -tz "Europe/Madrid" -t fast-ts -c

# General TS
echo "Weather ts"
python3 -m harmonizer -so Weather -n "https://weather.beegroup-cimne.com#" -t fast-ts -c

echo "Datadis TS"
python3 -m harmonizer -so Datadis -n "https://icaen.cat#" -u icaen -t ts -c
echo "Nedgia"
python3 -m harmonizer -so Nedgia -n "https://icaen.cat#" -u icaen -tz "Europe/Madrid" -t ts -c

# General TS
echo "Weather ts"
python3 -m harmonizer -so Weather -n "https://weather.beegroup-cimne.com#" -t ts -c


# create Device AGGREGATORS

echo "DeviceAggregators datadis"
python3 -m set_up.DeviceAggregator -t "totalElectricityConsumption"
echo "DeviceAggregators nedgia"
python3 -m set_up.DeviceAggregator -t "totalGasConsumption"
echo "DeviceAggregators weather"
python3 -m set_up.DeviceAggregator -t "externalWeather"

# LOAD DATA KAFKA
python3 -m gather -so GPG -f "data/GPG/Llistat immobles alta inventari (13-04-2021).xls" -n "https://icaen.cat#" -st kafka -u icaen
python3 -m gather -so Gemweb -st kafka
python3 -m gather -so Genercat -f data/genercat/data2.xls -u icaen -n "https://icaen.cat#" -st kafka
python3 -m gather -so Datadis
python3 -m gather -so Weather



#INFRAESTRUCTURES ORGANIZATION "https://infraestructures.cat#"
# SET UP
python3 -m set_up.Organizations -f data/Organizations/infraestructures-organizations.xls -name "Infraestructures.cat" -u "icat" -n "https://infraestructures.cat#"

# LOAD DATA HBASE
python3 -m harmonizer -so BIS -u "icat" -n "https://infraestructures.cat#" -c

# LOAD DATA KAFKA

python3 -m gather -so BIS -f "data/BIS/BIS-infraestructures.xls" -u "icat" -n "https://infraestructures.cat#" -st kafka


# BULGARIA ORGANIZATION "https://bulgaria.bg#"
# SET UP
python3 -m set_up.Organizations -f data/Organizations/bulgaria-organizations.xls -name "Bulgaria" -u "bulgaria" -n "https://bulgaria.bg#"

# LOAD DATA HBASE

python3 -m harmonizer -so Bulgaria -u "bulgaria" -n "https://bulgaria.bg#" -c


# LOAD DATA KAFKA


python3 -m gather -so Bulgaria -f "data/Bulgaria" -u "bulgaria" -n "https://bulgaria.bg#" -t summary -st kafka


# Greece Organization
python3 -m gather -n "https://eplanet.eu#" -so Greece -st kafka -u Greece -f "data/crete"


# Czech
python3 -m gather -n "https://eplanet.eu#" -so Czech -st kafka -u eplanet -f data/czech/building -kf building_eem
