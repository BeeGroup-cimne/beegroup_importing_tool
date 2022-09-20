# Install Neo4j

Follow the instruction in the [link](https://neo4j.com/docs/operations-manual/current/installation/linux/debian/#debian-installation)

Add in the `plugins` directory located at `/var/lib/neo4j/plugins`:
 - the neosemantics
 - the apoc

if you face the error `NoSuchMethodError` with `apoc.convert.fromJsonList`, follow the instruction in the [link](https://github.com/neo4j-contrib/neo4j-apoc-procedures/issues/2861)

# Set up the database (first time)
- login and change the password.
- run in neo4j:
```cypher 
CREATE CONSTRAINT n10s_unique_uri ON (r:Resource) ASSERT r.uri IS UNIQUE
```
# Set up the database (all the time after reset)
- run in neo4j:
```cypher
CALL n10s.graphconfig.init({ keepLangTag: true, handleMultival:"ARRAY", multivalPropList:["http://www.w3.org/2000/01/rdf-schema#label", "http://www.w3.org/2000/01/rdf-schema#comment", "http://www.geonames.org/ontology#officialName"]});
CALL n10s.nsprefixes.add("bigg","http://bigg-project.eu/ontology#");
CALL n10s.nsprefixes.add("geo","http://www.geonames.org/ontology#");
CALL n10s.nsprefixes.add("unit","http://qudt.org/vocab/unit/");
CALL n10s.nsprefixes.add("wgs","http://www.w3.org/2003/01/geo/wgs84_pos#");
CALL n10s.nsprefixes.add("rdfs","http://www.w3.org/2000/01/rdf-schema#");
```
- run in linux terminal
```bash
# Create the dictionary of elements
echo "dict"
python3 -m set_up.Dictionaries
# add translation labels
python3 -m utils.rdf_utils.ontology.taxonomy_translations  translate
```
# General Setup
```bash
# create the weather stations (for each country)
echo "weather stations catalonia"
python3 -m set_up.Weather -f data/Weather/cpcat.json -n "https://weather.beegroup-cimne.com#" -c
```
# SETUP by Organization

----
## ICAEN ORGANIZATION 
 - namespace: `https://icaen.cat#`
 - username: `icaen`

### 1. SET UP
```bash
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
echo "co2Emisions source"
python3 -m set_up.DataSources -u "icaen" -n "https://icaen.cat#" -f data/DataSources/simpleTariff.xls -d C02EmissionsSource
```

### 2. LOAD STATIC DATA
2.1 Load from HBASE
```bash
echo "GPG"
python3 -m harmonizer -so GPG -u "icaen" -n "https://icaen.cat#" -o -c
echo "Gemweb"
python3 -m harmonizer -so Gemweb -u "icaen" -n "https://icaen.cat#" -c
echo "Genercat"
python3 -m harmonizer -so Genercat -u "icaen" -n "https://icaen.cat#" -c
echo "Datadis static"
python3 -m harmonizer -so Datadis -n "https://icaen.cat#" -u icaen -t static -c
python3 -m harmonizer -so CEEC3X -n "https://icaen.cat#" -u icaen -c
```
2.2 Load from KAFKA
```bash
python3 -m gather -so GPG -f "data/GPG/Llistat immobles alta inventari (13-04-2021).xls" -n "https://icaen.cat#" -st kafka -u icaen
python3 -m gather -so Gemweb -st kafka
python3 -m gather -so Genercat -f data/genercat/data2.xls -u icaen -n "https://icaen.cat#" -st kafka
python3 -m gather -so Datadis # MR-Job
python3 -m gather -so Weather # MR-Job
```
### 3. Create a new Tariff and co2Emissions for the organization
```cypher
Match (o:bigg__Organization{userID:"icaen"})
Match (s:SimpleTariffSource) where (s)<-[:hasSource]-(o)
Merge (t:bigg__Tariff{bigg__tariffCompany:"CIMNE", bigg__tariffName: "electricdefault", uri: "https://icaen.cat#TARIFF-SimpleTariffSource-icaen-electricdefault"})-[:importedFromSource]->(s)
return t;
Match (o:bigg__Organization{userID:"icaen"})
Match (s:SimpleTariffSource) where (s)<-[:hasSource]-(o)
Merge (t:bigg__Tariff:Resource{bigg__tariffCompany:"CIMNE", bigg__tariffName: "gasdefault", uri: "https://icaen.cat#TARIFF-SimpleTariffSource-icaen-gasdefault"})-[:importedFromSource]->(s)
return t;
Match (o:bigg__Organization{userID:"icaen"})
Match (s:C02EmissionsSource) where (s)<-[:hasSource]-(o)
Merge (t:bigg__CO2EmissionsFactor:Resource{bigg__CO2EmissionsStation:"cataloniaElectric", wgs__lon:40.959, wgs__lat:1.485, uri: "https://weather.beegroup-cimne.com#CO2EMISIONS-cataloniaElectric"})-[:importedFromSource]->(s)
return t;
Match (o:bigg__Organization{userID:"icaen"})
Match (s:C02EmissionsSource) where (s)<-[:hasSource]-(o)
Merge (t:bigg__CO2EmissionsFactor:Resource{bigg__CO2EmissionsStation:"cataloniaGas", wgs__lon:40.959, wgs__lat:1.485, uri: "https://weather.beegroup-cimne.com#CO2EMISIONS-cataloniaGas"})-[:importedFromSource]->(s)
return t;
```
### 4. Link all buildings to tariff and CO2Emissions
```
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
```

### 5. Link building with the closest Weather Station
```bash
echo "Link WS with Buildings"
python3 -m set_up.Weather -f data/Weather/cpcat.json -n "https://weather.beegroup-cimne.com#" -u
```

### 6. Load Timeseries Data

6.1. Load TS (only links)
```bash
echo "Datadis TS"
python3 -m harmonizer -so Datadis -n "https://icaen.cat#" -u icaen -t fast-ts -c
echo "Nedgia"
python3 -m harmonizer -so Nedgia -n "https://icaen.cat#" -u icaen -tz "Europe/Madrid" -t fast-ts -c
echo "Weather ts"
python3 -m harmonizer -so Weather -n "https://weather.beegroup-cimne.com#" -t fast-ts -c
```
6.2. Load TS (harmonize full timeseries)
```bash
echo "Datadis TS"
python3 -m harmonizer -so Datadis -n "https://icaen.cat#" -u icaen -t ts -c
echo "Nedgia"
python3 -m harmonizer -so Nedgia -n "https://icaen.cat#" -u icaen -tz "Europe/Madrid" -t ts -c
echo "Weather ts"
python3 -m harmonizer -so Weather -n "https://weather.beegroup-cimne.com#" -t ts -c
```

### 7. Create Device AGGREGATORS
```bash
echo "DeviceAggregators datadis"
python3 -m set_up.DeviceAggregator -t "totalElectricityConsumption"
echo "DeviceAggregators nedgia"
python3 -m set_up.DeviceAggregator -t "totalGasConsumption"
echo "DeviceAggregators weather"
python3 -m set_up.DeviceAggregator -t "externalWeather"
```

----
## INFRAESTRUCTURES ORGANIZATION 
 - namespace: `https://infraestructures.cat#`
 - username: `icat`

### 1. SET UP
```bash
python3 -m set_up.Organizations -f data/Organizations/infraestructures-organizations.xls -name "Infraestructures.cat" -u "icat" -n "https://infraestructures.cat#"
```
### 2. LOAD STATIC DATA
2.1 Load from HBASE
```bash
python3 -m harmonizer -so BIS -u "icat" -n "https://infraestructures.cat#" -c
```
2.2 Load to Kafka
```bash
python3 -m gather -so BIS -f "data/BIS/BIS-infraestructures.xls" -u "icat" -n "https://infraestructures.cat#" -st kafka
```
----
## BULGARIA ORGANIZATION 
 - namespace: `https://bulgaria.bg#`
 - username: `bulgaria`

### 1. SET UP
```bash
echo "main org"
python3 -m set_up.Organizations -f data/Organizations/bulgaria-organizations.xls -name "Bulgaria" -u "bulgaria" -n "https://bulgaria.bg#"
echo "summary source"
python3 -m set_up.DataSources -u "bulgaria" -n "https://bulgaria.bg#" -f data/DataSources/bulgaria.xls -d SummarySource

```
### 2. LOAD STATIC DATA
2.1 Load from HBASE
```bash
python3 -m harmonizer -so Bulgaria -u "bulgaria" -n "https://bulgaria.bg#" -c
```
2.2 Load to Kafka
```bash
python3 -m gather -so Bulgaria -f "data/Bulgaria" -u "bulgaria" -n "https://bulgaria.bg#" -t summary -st kafka
```