import re
from functools import partial


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
    return f"{source}-DEVICE-{key}"


def delivery_subject(key):
    return f"SUPPLY-{key}"


def device_raw_measure_subject(key, source):
    return f"{source}-DEVICE-RAW-{key}"


def validate_ref_cadastral(value):
    ref = value.split(";")
    valid_ref = []
    for refer in ref:
        refer = refer.strip()
        match = re.match("[0-9A-Z]{20}", refer)
        if match:
            valid_ref.append(match[0])
    return ";".join(valid_ref)





