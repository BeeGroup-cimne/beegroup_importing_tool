# Genercat description
Genercat(Energy Eficiency Measures) is an application to describe the energy efficiency measures (eem) applied in buildings and properties
belonging to the Generalitat de Catalunya. 

## Gathering tool
This data source comes in the format of an Excel file where each row is the information about a EEM.+

## Raw Data Format

Each row contains information about an eem with no previous ID. For instance, the ID will be generated as 
the checksum of the filename and the row where the measure is in the file `<checksum>~<row>`.

| Source   | class | Hbase key    |
|----------|-------|--------------|
| Genercat | eem   | checksum~row |

*Mapping key from Genercat source*

## Import script information

For each import run, the information stored regarding the status of this import will be a document containing the 
following information:
```json
{
    "user" : "the user that imported data",
    "logs": {
      "gather" : "list with the logs of the import",
      "logs.store" : "list with the logs of the store",
      "logs.harmonize" : "list with the logs of the harmonization"
    },
    "log_exec": "timestamp of execution"
}
```


## RUN import application
To run the import application, execute the python script with the following parameters:

```bash
python3 -m gather -so Genercat -f <genercat file> -n <namespace> -u <user_importing> -st <storage>
```