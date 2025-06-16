from cgitb import reset

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
        self.add_enter_socket('Сигма', self.palette['NUM'])

        self.add_output_socket('', self.palette['NUM'])

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

        result = result_down / result_up

        self.output_sockets[''].set_value(result)

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Расщепление', 'Metric'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
