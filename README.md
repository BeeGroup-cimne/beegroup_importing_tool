# Import raw data to the system

TThis project has the infrastructure to import and harmonize different data sources.

The architecture used for the import and harmonization of the sources is as follows:
<img src="docs/schema_diagram.svg"/>

The different components of the architecture are depicted in the following list:
## Install the package:
   1. Install the application to your environment
   2. Place the dictionaries in the dict_folder `ontology/dictionaries`
   3. Run to generate the ontology `python3 -m main_ontology`

# PREPARE THE PROJECT:
Create the directories `ontology`, `sources` and `translations`, write the `settings.py` and `set_up_params.py` files

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

## Setup Neo4j Database
To get the Neo4j database working, we need to use [Neosemantics] (https://neo4j.com/labs/neosemantics/4.0/) plugin 

1. Create a unique constraint on uri:
    ```
    CREATE CONSTRAINT n10s_unique_uri ON (r:Resource)
    ASSERT r.uri IS UNIQUE;
    ```
2. Create the graph configuration:
    ```
     CALL n10s.graphconfig.init({ keepLangTag: true, handleMultival:"ARRAY", multivalPropList:[<list of multival values>]});
    ```
3. Add the namespaces we will use:
    ```
    CALL n10s.nsprefixes.add("<namespace>","<uri_namespace>");
    CALL n10s.nsprefixes.add("geo","http://www.geonames.org/ontology#");
    CALL n10s.nsprefixes.add("wgs","http://www.w3.org/2003/01/geo/wgs84_pos#");
    CALL n10s.nsprefixes.add("unit","http://qudt.org/vocab/unit/");
    ```

## Configuration

The configuration file for running the applications consists of a config.json that must be placed in the root of the project and add the source specific configuration

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
