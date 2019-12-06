__copyright__ = "Copyright 2019, RISE Research Institutes of Sweden"
__author__ = "Naveed Anwar Bhatti and Martina Brachmann"


def maprange(a, b, s):
    '''
    Maps an input value to an ouput value depending on a sensors' and actuators's range

    Parameters
    ----------
    a : tupel (float, float)
        the sensors' known/given range (from, to)
    b : tupel (float, float)
        the actuators' known/given range (from, to)
    s : float
        current input value

    Returns
    -------
    float : the mapped value
    '''
    (a1, a2), (b1, b2) = a, b
    return b1 + ((s - a1) * (b2 - b1) / (a2 - a1))


def maprange_by_factor(a, b, s, fac):
    return maprange(a, b, s * fac)


def maprange_by_hop_factor(a, b, s, h_f):
    (hops, factor) = h_f
    fac = 1
    for hop in range(1, hops+1):
        factor = factor / hop
        fac = fac + factor
    return maprange_by_factor(a, b, s, fac)


def maprange_by_neighbor(a, b, s, neighbor):
    pass