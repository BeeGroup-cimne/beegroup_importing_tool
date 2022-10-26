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
echo "create dictionaries"
python3 -m set_up.Dictionaries
echo "add translation labels"
python3 -m utils.rdf_utils.ontology.taxonomy_translations  translate
```
# TODO
# General Setup
```bash
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
python3 -m set_up.Organizations -f data/Organizations/gencat-organizations2.xls -name "Generalitat de Catalunya" -u "icaen" -n "https://icaen.cat#"
echo "Gemweb source"
python3 -m set_up.DataSources -u "icaen" -n "https://icaen.cat#" -f data/DataSources/gemweb.xls -d GemwebSource
echo "datadis source"
python3 -m set_up.DataSources -u "icaen" -n "https://icaen.cat#" -f data/DataSources/datadis.xls -d DatadisSource
echo "nedgia source"
python3 -m set_up.DataSources -u "icaen" -n "https://icaen.cat#" -f data/DataSources/nedgia.xls -d NedgiaSource
echo "simpleTariff source"
python3 -m set_up.DataSources -u "icaen" -n "https://icaen.cat#" -f data/DataSources/simpleTariff.xls -d SimpleTariffSource
echo "co2Emisions source"
python3 -m set_up.DataSources -u "icaen" -n "https://icaen.cat#" -f data/DataSources/simpleTariff.xls -d CO2EmissionsSource
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
python3 -m harmonizer -so OpenData -n "https://icaen.cat#" -u icaen -c
```
2.2 Load from KAFKA
```bash
python3 -m gather -so GPG -f "data/GPG/2022-10 SIME-DadesdelsImmobles v2.xlsx" -n "https://icaen.cat#" -st kafka -u icaen
python3 -m gather -so Gemweb -st kafka
python3 -m gather -so Genercat -f data/genercat/data2.xls -u icaen -n "https://icaen.cat#" -st kafka
python3 -m gather -so CEEC3X -f "data/CEEC3X/ceec3x-01639-2TX229LJ9.xml" -b 01639 -id 2TX229LJ9 -n "https://icaen.cat#" -u icaen  -st kafka

python3 -m gather -so Datadis # MR-Job
python3 -m gather -so Weather # MR-Job
python3 -m gather -so OpenData -n "https://icaen.cat#" -u icaen -c

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
Match (s:CO2EmissionsSource) where (s)<-[:hasSource]-(o)
Merge (t:bigg__CO2EmissionsFactor:Resource{bigg__CO2EmissionsStation:"cataloniaElectric", wgs__lon:40.959, wgs__lat:1.485, uri: "https://icaen.cat#CO2EMISIONS-cataloniaElectric"})-[:importedFromSource]->(s)
return t;
Match (o:bigg__Organization{userID:"icaen"})
Match (s:CO2EmissionsSource) where (s)<-[:hasSource]-(o)
Merge (t:bigg__CO2EmissionsFactor:Resource{bigg__CO2EmissionsStation:"cataloniaGas", wgs__lon:40.959, wgs__lat:1.485, uri: "https://icaen.cat#CO2EMISIONS-cataloniaGas"})-[:importedFromSource]->(s)
return t;
```
### 4. Link all buildings to tariff and CO2Emissions
```
Match (bigg__Organization{userID:"icaen"})-[:hasSource]->(:SimpleTariffSource)<-[:importedFromSource]-(t:bigg__Tariff{bigg__tariffName:"electricdefault"})
Match (dt {uri:"http://bigg-project.eu/ontology#Electricity"})
Match (bigg__Organization{userID:"icaen"})-[:bigg__hasSubOrganization*]->()-[:bigg__managesBuilding]->()-[:bigg__hasSpace]->()-[:bigg__hasUtilityPointOfDelivery]->(s)-[:bigg__hasUtilityType]->(dt)
Merge (c:bigg__ContractedTariff:Resource{bigg__contractStartDate: datetime("2000-01-01T00:00:00.000+0100"), bigg__contractName:"electricdefault", uri: s.uri+"_tariff"})
Merge (s)-[:bigg__hasContractedTariff]->(c)
Merge (c)-[:bigg__hasTariff]->(t)
return t;
Match (bigg__Organization{userID:"icaen"})-[:hasSource]->(:SimpleTariffSource)<-[:importedFromSource]-(t:bigg__Tariff{bigg__tariffName:"gasdefault"})
Match (dt {uri:"http://bigg-project.eu/ontology#Gas"})
Match (bigg__Organization{userID:"icaen"})-[:bigg__hasSubOrganization*]->()-[:bigg__managesBuilding]->()-[:bigg__hasSpace]->()-[:bigg__hasUtilityPointOfDelivery]->(s)-[:bigg__hasUtilityType]->(dt)
Merge (c:bigg__ContractedTariff:Resource{bigg__contractStartDate: datetime("2000-01-01T00:00:00.000+0100"), bigg__contractName:"gasdefault", uri: s.uri+"_tariff"})
Merge (s)-[:bigg__hasContractedTariff]->(c)
Merge (c)-[:bigg__hasTariff]->(t)
return t;
Match (bigg__Organization{userID:"icaen"})-[:hasSource]->(:CO2EmissionsSource)<-[:importedFromSource]-(co2:bigg__CO2EmissionsFactor{bigg__CO2EmissionsStation:"cataloniaElectric"})
Match (dt {uri:"http://bigg-project.eu/ontology#Electricity"})
Match (bigg__Organization{userID:"icaen"})-[:bigg__hasSubOrganization*]->()-[:bigg__managesBuilding]->()-[:bigg__hasSpace]->()-[:bigg__hasUtilityPointOfDelivery]->(s)-[:bigg__hasUtilityType]->(dt)
Merge (s)-[:bigg__hasCO2EmissionsFactor]->(co2)
return co2;
Match (bigg__Organization{userID:"icaen"})-[:hasSource]->(:CO2EmissionsSource)<-[:importedFromSource]-(co2:bigg__CO2EmissionsFactor{bigg__CO2EmissionsStation:"cataloniaGas"})
Match (dt {uri:"http://bigg-project.eu/ontology#Gas"})
Match (bigg__Organization{userID:"icaen"})-[:bigg__hasSubOrganization*]->()-[:bigg__managesBuilding]->()-[:bigg__hasSpace]->()-[:bigg__hasUtilityPointOfDelivery]->(s)-[:bigg__hasUtilityType]->(dt)
Merge (s)-[:bigg__hasCO2EmissionsFactor]->(co2)
return co2;
```

### 5. load tariff and co2 timeseries
```bash
python3 -m harmonizer -so SimpleTariff -u icaen -mp "http://bigg-project.eu/ontology#Price.EnergyPriceGridElectricity" -pp "http://bigg-project.eu/ontology#EnergyConsumptionGridElectricity" -ppu "http://qudt.org/vocab/unit/KiloW-HR" -unit "http://qudt.org/vocab/unit/Euro" -n "https://icaen.cat#" -c 
python3 -m harmonizer -so SimpleTariff -u icaen -mp "http://bigg-project.eu/ontology#Price.EnergyPriceGas" -pp "http://bigg-project.eu/ontology#EnergyConsumptionGas" -ppu "http://qudt.org/vocab/unit/KiloW-HR" -unit "http://qudt.org/vocab/unit/Euro" -n "https://icaen.cat#" -c 
python3 -m harmonizer -so CO2Emissions -mp "http://bigg-project.eu/ontology#CO2Emissions" -p "http://bigg-project.eu/ontology#EnergyConsumptionGridElectricity" -pu "http://qudt.org/vocab/unit/KiloW-HR" -u "http://qudt.org/vocab/unit/KiloGM" -n "https://icaen.cat#" -c 
python3 -m harmonizer -so CO2Emissions -mp "http://bigg-project.eu/ontology#CO2Emissions" -p "http://bigg-project.eu/ontology#EnergyConsumptionGas" -pu "http://qudt.org/vocab/unit/KiloW-HR" -u "http://qudt.org/vocab/unit/KiloGM" -n "https://icaen.cat#" -c 

```
### 6. Link building with the closest Weather Station
```bash
echo "Link WS with Buildings"
python3 -m set_up.Weather -f data/Weather/cpcat.json -n "https://weather.beegroup-cimne.com#" -u
```

### 7. Load Timeseries Data

7.1. Load TS (only links)
```bash
echo "Datadis TS"
python3 -m harmonizer -so Datadis -n "https://icaen.cat#" -u icaen -t fast-ts -c
echo "Nedgia"
python3 -m harmonizer -so Nedgia -n "https://icaen.cat#" -u icaen -tz "Europe/Madrid" -t fast-ts -c
echo "Weather ts"
python3 -m harmonizer -so Weather -n "https://weather.beegroup-cimne.com#" -t fast-ts -c
```
7.2. Load TS (harmonize full timeseries)
```bash
echo "Datadis TS"
python3 -m harmonizer -so Datadis -n "https://icaen.cat#" -u icaen -t ts -c
echo "Nedgia"
python3 -m harmonizer -so Nedgia -n "https://icaen.cat#" -u icaen -tz "Europe/Madrid" -t ts -c
echo "Weather ts"
python3 -m harmonizer -so Weather -n "https://weather.beegroup-cimne.com#" -t ts -c
```

### 8. Create Device AGGREGATORS
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
### 3. Link building with the closest Weather Station
```bash
echo "Link WS with Buildings"
python3 -m set_up.Weather -f data/Weather/cpcat.json -n "https://weather.beegroup-cimne.com#" -u
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