def raw_nomenclature(source, mode, data_type="", frequency="", user=""):
    return f"raw_{source}_{mode}_{data_type}_{frequency}_{user}"


def harmonized_nomenclature(mode, data_type, R, C, O, aggregation_function="", freq='', user=''):
    return f"harmonized_{mode}_{data_type}_{bool_to_int(R)}{bool_to_int(C)}{bool_to_int(O)}_{aggregation_function}_{freq}_{user}"


def bool_to_int(value):
    return int(value == True)
