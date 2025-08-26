

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

        self.add_output_socket('', self.palette['CAMERA_SHOT'])

        self.load_data = kwargs
        self.strong_control = False

    @staticmethod
    def extract_center_window(arr, window_size):

        rows, cols = arr.shape

        if window_size > rows or window_size > cols:
            raise ValueError("Размер окна не может быть больше размеров исходного массива")

        start_row = (rows - window_size) // 2
        end_row = start_row + window_size
        start_col = (cols - window_size) // 2
        end_col = start_col + window_size


        center_window = arr[start_row:end_row, start_col:end_col]

        return center_window


    def execute(self):
        arguments = self.get_func_inputs()

        image = arguments['Изображение']

        side = np.min(np.shape(image))

        result = self.extract_center_window(image, side)

        self.output_sockets[''].set_value(result)

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Full Frame', 'Metric'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
