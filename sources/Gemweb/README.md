# Gemweb description
Gemweb is an application to manage the invoices and increase energy efficiency of buildings and properties.

## Gathering tool
This data source comes in the format of an [API](http://manual.gemweb.es/), where different endpoints are available.
The gathering tool of datadis, will make use of the [beegweb](https://github.com/BeeGroup-cimne/beegweb) python library to obtain the data.

## Raw Data Format
The data imported will be stored in the Hbase table for each endpoint, the row key of each endpoint will be as follows.

Inventory entities will be considered "static data", as they mainly will remain the same.

Each static element has a gemweb internal `id` wich we will use to unequivocally identify the 
element. Future changes on the element will override the previous values. The rest of the file columns for each entity
will be mapped to the column family `info` with column using the raw format name.

For the timeseries type of data, the key document will be a concatenation of the id field and the timestamp or date 
of the element. This data will be appended everytime, and we will only update the previous values when some change will
be applied to previous data.

| Source  |  class    | Hbase key          |
|---------|-----------|--------------------|
| gemweb  |  building |        id          |
| gemweb  |  entities |        id          | 
| gemweb  |  supplies |        id          |
| gemweb  |  invoices |      id~d_mod      |
| gemweb  |time-series|    id~timestamp    |

*Mapping keys from Gemweb source*

## Import script information

For each static data import run, the information stored regarding the status of this import will be a document containing the 
following information:
```json
{
    "user" : "the user that imported data",
    "user_datasource": "the username of the user importing the data",
    "logs": {
      "gather" : "list with the logs of the import",
      "logs.store" : "list with the logs of the store",
      "logs.harmonize" : "list with the logs of the harmonization"
    },
    "log_exec": "timestamp of execution"
}
```
For the timeseries, we will contain a document for each imported device and each granularity, the information contained will be:
**USER BANNED**
```json

```

## RUN import application
To run the import application, execute the python script with the following parameters:

**USER BANNED**

[//]: # (```bash)

[//]: # (## import static data)

[//]: # (#python Gemweb/gemweb_gather.py -d <data_type>)

[//]: # (## where data_type can be one of ['entities', 'buildings', 'solarpv', 'supplies', 'invoices'])

[//]: # (#)

[//]: # (## import timeseries)

[//]: # (#python Gemweb/timeseries_gather.py)

[//]: # (```)