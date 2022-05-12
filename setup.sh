# CREATE CONSTRAINT n10s_unique_uri ON (r:Resource) ASSERT r.uri IS UNIQUE
# CALL n10s.graphconfig.init({ keepLangTag: true, handleMultival:"ARRAY"});
# CALL n10s.nsprefixes.add("bigg","http://bigg-project.eu/ontology#");
# CALL n10s.nsprefixes.add("geo","http://www.geonames.org/ontology#");
# CALL n10s.nsprefixes.add("unit","http://qudt.org/vocab/unit/");
# CALL n10s.nsprefixes.add("wgs","http://www.w3.org/2003/01/geo/wgs84_pos#");
# CALL n10s.nsprefixes.add("ttt","http://ttt.cat#");

echo "dict"
python3 -m set_up.Dictionaries
echo "org"
python3 -m set_up.Organizations -f data/Organizations/organizations.xls -name "Generalitat de Catalunya" -u "icaen" -n "https://icaen.cat#"
echo "Gemweb"
python3 -m set_up.DataSources -u "icaen" -n "https://icaen.cat#" -f data/DataSources/gemweb.xls -d GemwebSource
echo "datadis"
python3 -m set_up.DataSources -u "icaen" -n "https://icaen.cat#" -f data/DataSources/datadis.xls -d DatadisSource
echo "nedgia"
python3 -m set_up.DataSources -u "icaen" -n "https://icaen.cat#" -f data/DataSources/nedgia.xls -d NedgiaSource
echo "weather"
python3 -m set_up.Weather -f data/Weather/cpcat.json -n "https://weather.beegroup-cimne.com#" -c
echo "GPG"
python3 -m harmonizer -so GPG -u "icaen" -n "https://icaen.cat#" -o -c
echo "Gemweb"
python3 -m harmonizer -so Gemweb -u "icaen" -n "https://icaen.cat#" -c
echo "Gemweb"


