from Blocks import ValueMapping


__copyright__ = "Copyright 2019, RISE Research Institutes of Sweden"
__author__ = "Naveed Anwar Bhatti and Martina Brachmann"


def indirect_mapping(range_sensor, range_actuator, input, arg):
    value = ValueMapping.maprange_by_factor(range_sensor, range_actuator, input, 2)
    return value