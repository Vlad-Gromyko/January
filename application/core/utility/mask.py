import numpy as np
from PIL import Image


class Mask:
    def __init__(self, array: np.ndarray):
        self._array = self.transform_to_2pi(array)

    def get_array(self) -> np.ndarray:
        return self._array

    @staticmethod
    def transform_to_2pi(array):
        min_value = np.min(array)
        if min_value < 0:
            array = array - min_value

        array = array % (2 * np.pi)
        return array

    def __add__(self, other):
        other_array = other.get_array()
        new_array = self._array + other_array
        new_array = self.transform_to_2pi(new_array)
        return Mask(new_array)

    def __sub__(self, other):
        other_array = other.get_array()
        new_array = self._array - other_array
        new_array = self.transform_to_2pi(new_array)
        return Mask(new_array)

    def __mul__(self, other):
        other_array = other.get_array()
        new_array = self._array * other_array
        new_array = self.transform_to_2pi(new_array)
        return Mask(new_array)



