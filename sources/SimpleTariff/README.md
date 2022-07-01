# Simple Tariff Documentation

The tariff will be created as a common tariff in the organization, where each Building will be able to be linked to it.

The Organization owner will upload data to the tariff, with the possibility of changing the price.

The OADMIN will upload a file, always containing 8784 rows, each one related to an hour in a year.
If the day does not exist in the year (29-2) the rows related to this time will be ignored.

The OADMIN will indicate the effect time of this file (no overlaps will be allowed).
The data will be replicated for all the time, if several years are indicated, at the same time and hour.

Each tariff will have a list of uploaded files, and the periods they are affecting.
METADATA:
tariff_related.
    -File with 8784 rows
    -start_date -> end_date
