from Blocks import ValueMapping


__copyright__ = "Copyright 2019, RISE Research Institutes of Sweden"
__author__ = "Naveed Anwar Bhatti and Martina Brachmann"


def direct_mapping(range_sensor, range_actuator, input, arg):
    value = ValueMapping.maprange(range_sensor, range_actuator, input)
    return value