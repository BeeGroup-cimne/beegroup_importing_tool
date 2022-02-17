# Import raw data to the system

TThis project has the infrastructure to import and harmonize different data sources.

The architecture used for the import and harmonization of the sources is as follows:
<img src="docs/schema_diagram.svg"/>

The different components of the architecture are depicted in the following list:

## External API Producer

This component is in charge to communicate to the different external providers and make the pertinent requests to obtain the data. This component is able to store the data directly to *HBASE* or send it to the *KAFKA* to be processed later. 

The idea behind this import of raw data is to save the information with minimal changes and transformations, providing
permanent access to the raw data obtained from each source.

```bash
python -m gather -so <source> [-kargs args]
```

## Raw Data Storage

This component consumes the raw data from *KAFKA* and stores its components directly to *HBASE*. 
This is done to always keep the original information without any modification.

To start the storage application
```bash
python3 -m store
```

## Harmonize Consumer
This component consumes the raw data from *KAFKA* or *HBASE* and applies the harmonization to transform this data to the data model. 
Finally, it stores the data in *Neo4j* or *HBASE* as required.

To start the harmonization application
```bash
python3 -m harmonizer
```

## Data sources index

The following links will provide information of each data source import tool:

1. [GPG (Gestió de patrimoni de la generalitat)](sources/GPG/README.md)
2. [Gemweb](sources/Gemweb/README.md)
3. [Datadis](sources/Datadis/README.md)
4. [Genercat](sources/genercat/README.md)
5. [Weather](sources/Weather/README.md)


## Setup sources
The following are some scripts to automatically set up some of the features from organizations in BIGG
1. Organizations
2. DataSources
3. WeatherStations.

[//]: # (5. [IXON]&#40;Ixon/README.md&#41;)
[//]: # (6. [Certificats d’eficiència energètica d’edificis]&#40;DadesObertes/CEEE/README.md&#41;)


## Configuration

The configuration file for running the applications consists of a config.json that must be placed in the root of the project

```json
{
  "mongo_db": {
    "host": "",
    "user": "",
    "pwd": "",
    "db": "",
    "port":""
  },
  "neo4j": {
    "uri": "",
    "auth": ["", ""]
  },
  "hbase_store_raw_data": {
    "host": "",
    "port": "",
    "table_prefix": "",
    "table_prefix_separator": ":"
  },
  "hbase_store_harmonized_data": {
    "host": "",
    "port": "",
    "table_prefix": "",
    "table_prefix_separator": ":"
  },
  "kafka": {
    "connection": {
      "hosts": [""],
      "ports": []
    },
    "topic": "",
    "group_harmonize": "",
    "group_store": ""
  },
  "encrypt_pass": {
      "environment": ""
  }
}
```
