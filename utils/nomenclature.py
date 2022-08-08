from enum import Enum


class RAW_MODE(Enum):
    STATIC = "static"
    TIMESERIES = "ts"


class HARMONIZED_MODE(Enum):
    ONLINE = "online"
    BATCH = "batch"


def raw_nomenclature(source, mode, data_type="", frequency="", user=""):
    if not isinstance(mode, RAW_MODE):
        raise Exception("Mode must be enum")
    return f"raw_{source}_{mode.value}_{data_type}_{frequency}_{user}"


def harmonized_nomenclature(mode, data_type, R, C, O, aggregation_function="", freq='', user=''):
    if not isinstance(mode, HARMONIZED_MODE):
        raise Exception("Mode must be enum")
    return f"harmonized_{mode.value}_{data_type}_{bool_to_int(R)}{bool_to_int(C)}{bool_to_int(O)}_{aggregation_function}_{freq}_{user}"


def bool_to_int(value):
    return int(value == True)
