from cgitb import reset

import customtkinter as ctk
import os
from application.core.events import Event
from application.core.services.nodes.node import INode
from application.core.utility.mask import Mask
from tkinter.filedialog import askdirectory
from matplotlib import cm
from PIL import Image

import numpy as np


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_output_socket('', self.palette['HOLOGRAM'])

        self.load_data = kwargs
        self.strong_control = True

    def execute(self):
        arguments = self.get_func_inputs()

        array = np.random.uniform(low=0, high=2 * np.pi, size=(1200, 1920))

        self.output_sockets[''].set_value(Mask(array))

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Рандом', 'Metric'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
