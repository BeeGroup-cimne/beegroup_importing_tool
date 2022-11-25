from enum import Enum


class RawMode(Enum):
    STATIC = "static"
    TIMESERIES = "ts"


class HarmonizedMode(Enum):
    ONLINE = "online"
    BATCH = "batch"


def raw_nomenclature(source, mode, data_type="", frequency="", user=""):
    if not isinstance(mode, RawMode):
        raise Exception("Mode must be RawMode instance")
    return f"raw_{source}_{mode.value}_{data_type}_{frequency}_{user}"


def harmonized_nomenclature(mode, data_type, R, C, O, aggregation_function="", freq='', user=''):
    if not isinstance(mode, HarmonizedMode):
        raise Exception("Mode must be HarmonizedMode instance")
    return f"harmonized_{mode.value}_{data_type}_{int(R)}{int(C)}{int(O)}_{aggregation_function}_{freq}_{user}"
