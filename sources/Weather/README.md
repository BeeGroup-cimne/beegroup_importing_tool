# Weather description
Weather data can be obtained from different weather sources

## Gathering tool
This data source comes in the format of different API and implementations.
The gathering tool of weather, will make use of the [beemeteo](https://github.com/BeeGroup-cimne/beemeteo) python 
library to obtain the data, where different sources are available.

## Raw Data Format
The data imported will be stored in the Hbase table automatically for the beemeteo library, so we are not going to use this
feature from the importing tool

## Import script information

For each import run a log document will be stored in mongo:
```json
{
    "logs": {
      "gather" : "list with the logs of the import",
      "logs.store" : "list with the logs of the store",
      "logs.harmonize" : "list with the logs of the harmonization"
    },
    "log_exec": "timestamp of execution"
}
```
Additionally, a set of collections for each timeseries device will be generated, to keep the status for each weather station.

```json
{
 "_id": "station id",
  "type of data": {
     "date_ini": "initial real data imported",
     "date_end": "final real data imported"
  }
}
```

## RUN import application
To run the import application, execute the python script with the following parameters:

```bash
python3 -m gather -so Weather -st <storage>
```
