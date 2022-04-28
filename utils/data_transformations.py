import re
from functools import partial

import pandas as pd
import rdflib
from thefuzz import process


def fuzzy_dictionary_match(text, dictionary, predicates):
    dicty = rdflib.Graph()
    dicty.load(dictionary, format="ttl")
    query = f"""SELECT ?s ?obj WHERE{{ {" UNION ".join([f"{{ ?s {p} ?obj }}" for p in predicates])} }}"""
    obj = dicty.query(query)
    map_dict = {o[1]: o[0] for o in obj}
    match, score = process.extractOne(text, list(map_dict.keys()))
    if score > 90:
        return map_dict[match]


def taxonomy_mapping(source_key, taxonomy_file, default):
    # Transformation function
    taxonomy_dict = \
        pd.read_excel(taxonomy_file, index_col="SOURCE").to_dict()["TAXONOMY"]
    try:
        return taxonomy_dict[source_key]
    except KeyError:
        return default


def to_object_property(text, namespace):
    return namespace[text]


def decode_hbase(value):
    if value is None:
        return ""
    elif isinstance(value, bytes):
        return value.decode()
    else:
        return str(value)


def join_params(args, joiner='~'):
    return joiner.join(args)


def zfill_param(key, num):
    return key.zfill(num)


id_zfill = partial(zfill_param, num=5)


def building_department_subject(key):
    return f"ORGANIZATION-{key}"


def building_subject(key):
    return f"BUILDING-{key}"


def building_space_subject(key):
    return f"BUILDINGSPACE-{key}"


def location_info_subject(key):
    return f"LOCATION-{key}"


def cadastral_info_subject(key):
    return f"CADASTRALINFO-{key}"


def __area_subject__(key, a_type, a_source):
    return f"AREA-{a_type}-{a_source}-{key}"


gross_area_subject = partial(__area_subject__, a_type="GrossFloorArea")
gross_area_subject_above = partial(__area_subject__, a_type="GrossFloorAreaAboveGround")
gross_area_subject_under = partial(__area_subject__, a_type="GrossFloorAreaUnderGround")


def construction_element_subject(key):
    return f"ELEMENT-{key}"


def eem_subject(key):
    return f"EEM-{key}"


def device_subject(key, source):
    return f"DEVICE-{source}-{key}"


def sensor_subject(device_source, device_key, measured_property, sensor_type, freq):
    return f"SENSOR-{device_source}-{device_key}-{measured_property}-{sensor_type}-{freq}"


def delivery_subject(key):
    return f"SUPPLY-{key}"


def validate_ref_cadastral(value):
    ref = value.split(";")
    valid_ref = []
    for refer in ref:
        refer = refer.strip()
        match = re.match("[0-9A-Z]{20}", refer)
        if match:
            valid_ref.append(match[0])
    return ";".join(valid_ref)


def epc_subject(key):
    return f"EPC-{key}"
