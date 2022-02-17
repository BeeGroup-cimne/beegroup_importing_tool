# Datadis description
Datadis(Datod de distribuïdora) is an application to obtain the energy consumption from the distribution company of spain.

## Gathering tool
This data source comes in the format of an [API](https://datadis.es/home), where different endpoints are available.
The gathering tool of datadis, will make use of the [beedis](https://github.com/BeeGroup-cimne/beedis) python library to obtain the data.

## Raw Data Format
The data imported will be stored in the Hbase table for each endpoint, the row key of each endpoint will be as follows.


| Source  | class     | Hbase key     |
|---------|-----------|---------------|
| Datadis | supplies  | cups          |
 | Datadis | data_1h   | cups~time_ini |
| Datadis | data_15m  | cups~time_ini |
| Datadis | max_power | cups~time_ini |

*Mapping key from Datadis source*

## Import script information

For each import run a log document will be stored in mongo:
```json
{
    "user" : "the user that imported data",
    "user_datasource": "the nif of the user importing the data",
    "logs": {
      "gather" : "list with the logs of the import",
      "logs.store" : "list with the logs of the store",
      "logs.harmonize" : "list with the logs of the harmonization"
    },
    "log_exec": "timestamp of execution"
}
```
Additionally, a set of collections for each timeseries device will be generated, splitting all the imported time period in
chunks and the status of importation of each chunk.

```json
{"_id": "cups for the device",
  "type of data": {
    "period": {
     "date_ini_block": "data_init for the block",
     "date_end_block": "date_end for the block",
     "values": "number of values obtained",
     "total": "total number of values",
     "retries": "retries for this chunk",
     "date_min": "minimum real data imported",
     "date_max": "maximum real data imported"
    }
   }
}
```

## RUN import application
To run the import application, execute the python script with the following parameters:

```bash
python3 -m gather -so Datadis -st <storage> -p <policy>
```
