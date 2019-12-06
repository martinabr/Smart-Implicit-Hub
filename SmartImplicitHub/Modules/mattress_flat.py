from Blocks import ValueMapping


__copyright__ = "Copyright 2019, RISE Research Institutes of Sweden"
__author__ = "Naveed Anwar Bhatti and Martina Brachmann"


def mattress_flat(range_sensor, range_actuator, input, arg):
    value = ValueMapping.maprange_by_hop_factor(range_sensor, range_actuator, input, arg)
    #value = ValueMapping.maprange(range_sensor, range_actuator, input)
    return value