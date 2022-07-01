from utils.data_transformations import load_dic


class Cache(object):
    country_dic = None
    province_dic = None
    municipality_dic = None

    @classmethod
    def load_cache(cls):
        cls.country_dic = load_dic(["utils/rdf_utils/ontology/dictionaries/countries.ttl"])
        cls.province_dic = load_dic(["utils/rdf_utils/ontology/dictionaries/province.ttl"])
        cls.municipality_dic = load_dic(["utils/rdf_utils/ontology/dictionaries/municipality.ttl"])
