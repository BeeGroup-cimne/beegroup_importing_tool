import set_up_params
from utils.data_transformations import load_dic


class Cache(object):

    @classmethod
    def load_cache(cls):
        cls.country_dic = load_dic(["ontology/dictionaries/countries.ttl"])
        for country in set_up_params.ZONE_DICTIONARY.keys():
            province_dic = load_dic([f"ontology/dictionaries/province_{country}.ttl"])
            exec(f'cls.province_dic_{country} = province_dic')
            municipality_dic = load_dic([f"ontology/dictionaries/municipality_{country}.ttl"])
            exec(f'cls.municipality_dic_{country} = municipality_dic')
