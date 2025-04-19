import numpy as np
import LightPipes as lp
import math


def zernike_by_number(number, rho, phi):
    number = (number + 1)
    n, m = lp.noll_to_zern(number)

    mabs = np.abs(m)
    prod = 1.0
    sign = 1
    summ = 0.0
    for s in range(int((n - mabs) / 2) + 1):
        if n - 2 * s != 0:
            prod = np.power(rho, n - 2 * s)
        else:
            prod = 1.0
        prod *= math.factorial(n - s) * sign
        prod /= (math.factorial(s)
                 * math.factorial(int(((n + mabs) / 2)) - s)
                 * math.factorial(int(((n - mabs) / 2)) - s))
        summ += prod
        sign = -sign
    if m >= 0:
        return summ * np.cos(m * phi)
    else:
        return (-1) * summ * np.sin(m * phi)
