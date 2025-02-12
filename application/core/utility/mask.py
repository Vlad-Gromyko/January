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


class MaskSaver:
    def __init__(self, mask_name, folder_path):
        self.mask_name = mask_name
        self.folder_path = folder_path

    def save_as_image(self, mask: Mask, file_format):
        array = np.asarray(mask.get_array() / 2 / np.pi * 255, dtype='uint8')
        image = Image.fromarray(array)
        image.save(self.folder_path + '/' + self.mask_name + file_format)

    def save_as_np(self, mask: Mask):
        array = mask.get_array()
        np.save(self.folder_path + '/' + self.mask_name + '.npy', array)

