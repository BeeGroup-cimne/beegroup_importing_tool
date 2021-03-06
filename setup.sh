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


echo "Link WS with Buildings"
python3 -m set_up.Weather -f data/Weather/cpcat.json -n "https://weather.beegroup-cimne.com#" -u


# load TS
echo "Datadis TS"
python3 -m harmonizer -so Datadis -n "https://icaen.cat#" -u icaen -t ts -c
echo "Nedgia"
python3 -m harmonizer -so Nedgia -n "https://icaen.cat#" -u icaen -tz "Europe/Madrid" -c

# General TS
echo "Weather ts"
python3 -m harmonizer -so Weather -n "https://weather.beegroup-cimne.com#" -c

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