

import customtkinter as ctk
import os
from application.core.events import Event
from application.core.services.nodes.node import INode
from tkinter.filedialog import askdirectory
from matplotlib import cm
from PIL import Image

import numpy as np

class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Изображение', self.palette['CAMERA_SHOT'])
        self.add_enter_socket('Размер окна', self.palette['NUM'])

        self.add_output_socket('', self.palette['CAMERA_SHOT'])

        self.load_data = kwargs
        self.strong_control = False

    @staticmethod
    def extract_center_window(arr, window_size):
        """
        Вырезает квадратное окно из центра исходного массива.

        Параметры:
        ----------
        arr : numpy.ndarray
            Исходный двумерный массив
        window_size : int
            Размер квадратного окна для вырезки

        Возвращает:
        -----------
        numpy.ndarray
            Квадратный массив с заданным размером окна, вырезанный из центра исходного
        """
        # Получаем размеры исходного массива
        rows, cols = arr.shape

        # Проверяем, что окно не больше исходного массива
        if window_size > rows or window_size > cols:
            raise ValueError("Размер окна не может быть больше размеров исходного массива")

        # Вычисляем начальные и конечные индексы для вырезки
        start_row = (rows - window_size) // 2
        end_row = start_row + window_size
        start_col = (cols - window_size) // 2
        end_col = start_col + window_size

        # Вырезаем центральное окно
        center_window = arr[start_row:end_row, start_col:end_col]

        return center_window


    def execute(self):
        arguments = self.get_func_inputs()

        image = arguments['Изображение']

        side = int(arguments['Размер окна'])

        result = self.extract_center_window(image, side)

        self.output_sockets[''].set_value(result)

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Frame', 'Metric'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
