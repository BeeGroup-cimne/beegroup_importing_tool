echo "dict"
python3 -m set_up.Dictionaries
echo "org"
python3 -m set_up.Organizations -f data/Organizations/organizations.xls -name "Generalitat de Catalunya" -u "icaen" -n "https://icaen.cat#"
echo "Gemweb"
python3 -m set_up.DataSources -name "Generalitat de Catalunya" -u "icaen" -n "https://icaen.cat#" -f data/DataSources/gemweb.xls -d GemwebSource
echo "datadis"
python3 -m set_up.DataSources -name "Generalitat de Catalunya" -u "icaen" -n "https://icaen.cat#" -f data/DataSources/datadis.xls -d DatadisSource
echo "weather"
python3 -m set_up.Weather -f data/Weather/cpcat.json -n "https://weather.beegroup-cimne.com#" -c

