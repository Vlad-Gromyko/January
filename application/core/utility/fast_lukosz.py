import numpy as np
import LightPipes as lp
import numba
import math

numba.njit(fastmath=True)


def noll_to_zern(j):
    j = j + 1
    n = 0
    j1 = j - 1
    while j1 > n:
        n += 1
        j1 -= n

    m = (-1) ** j * ((n % 2) + 2 * int((j1 + ((n + 1) % 2)) / 2.0))
    return n, m


numba.njit(fastmath=True)


def my_noll_to_zern(j):
    number = j
    j = j + 1
    n = 0
    j1 = j - 1
    while j1 > n:
        n += 1
        j1 -= n

    rr = np.arange(-n, n + 1, 2)

    pos = - n * (n + 1) // 2 + number

    m = int(rr[pos])

    return n, m


def radial_profile(n, m, rho):
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
    return summ


numba.njit(fastmath=True)


def lukosz_by_number(number, rho, phi):
    n, m = my_noll_to_zern(number)

    summ = 0

    if n == 0 and m == 0:
        summ = 1
    elif n==m and n != 0:
        summ = radial_profile(n, n, rho)
    elif n != m and n != 0 and n != m:
        summ = radial_profile(n, m, rho) - radial_profile(n-2, m, rho)
    elif n !=m and m == 0:
        summ = radial_profile(n, 0, rho) - radial_profile(n-2, 0, rho)


    if m >= 0:
        return summ * np.cos(m * phi)
    else:
        return (-1) * summ * np.sin(m * phi)


if __name__ == '__main__':

    for i in range(0, 20):
        print((my_noll_to_zern(i)))
