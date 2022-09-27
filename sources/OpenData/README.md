# Open Data - CEEE Dataset

CEEE (Certificats d’eficiència energètica d’edificis) is dataset of the energy certificates that are compulsory for the
existing buildings or dwellings in Catalonia.

## Gathering tool

This data source is obtained from the API, where we can obtain all the certificates.

#### RUN import application

To run the import application, execute the python script with the following parameters:

```bash
python3 -m gather -so OpenData -n <namespace> -st <storage> -u <user_importing>
```