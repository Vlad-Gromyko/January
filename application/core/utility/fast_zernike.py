import numpy as np
import LightPipes as lp
import numba
import math

numba.njit()
def noll_to_zern(j):


    n = 0
    j1 = j - 1
    while j1 > n:
        n += 1
        j1 -= n

    m = (-1) ** j * ((n % 2) + 2 * int((j1 + ((n + 1) % 2)) / 2.0))
    return n, m


numba.njit( fastmath=True)
def zernike_by_number(number, rho, phi):
    number = number + 1
    n, m = lp.noll_to_zern(number)

    mabs = np.abs(m)

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
