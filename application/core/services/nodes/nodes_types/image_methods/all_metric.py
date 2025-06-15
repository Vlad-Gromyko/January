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
        self.add_enter_socket('Порог', self.palette['NUM'])

        self.add_output_socket('Порог', self.palette['NUM'])
        self.add_output_socket('Симметрия', self.palette['NUM'])
        self.add_output_socket('MDS', self.palette['NUM'])
        self.add_output_socket('Произведение', self.palette['NUM'])



        self.load_data = kwargs
        self.strong_control = False

    def execute(self):
        arguments = self.get_func_inputs()

        image = arguments['Изображение']

        edge = arguments['Порог']

        result_up = np.where(image >= edge, image, 0)
        result_down = np.where(image < edge, image, 0)

        result_up = np.sum(result_up)
        result_down = np.sum(result_down)

        result_thresh = result_down / result_up

        self.output_sockets['Порог'].set_value(result_thresh)

        rotated_0 = np.flip(image, axis=0)
        rotated_1 = np.flip(image, axis=1)

        result_sym = np.sum(np.abs(image - rotated_0) + np.abs(image - rotated_1))

        self.output_sockets['Симметрия'].set_value(result_sym)

        w, h = np.shape(image)

        x = np.linspace(-h / 2, h / 2, h)
        y = np.linspace(-w / 2, w / 2, w)
        x, y = np.meshgrid(x, y)

        signal_intensity = np.sum(image * (x ** 2 + y ** 2))
        summ_intensity = np.sum(image)

        result_mds = signal_intensity / summ_intensity

        self.output_sockets['MDS'].set_value(result_mds)
        self.output_sockets['Произведение'].set_value(result_thresh + result_mds)

        print(result_thresh, result_sym, result_mds)

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Все-Метрика', 'Metric'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
