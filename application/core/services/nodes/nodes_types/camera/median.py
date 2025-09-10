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

        self.add_enter_socket('Снимки', self.palette['vector1d'])
        self.add_output_socket('Снимок', self.palette['CAMERA_SHOT'])


        self.load_data = kwargs
        self.strong_control = False


    def execute(self):
        arguments = self.get_func_inputs()

        shots = arguments['Снимки']

        shots = np.asarray(shots)

        processed = np.median(shots, axis=0)


        self.output_sockets['Снимок'].set_value(processed)



        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)


    @staticmethod
    def create_info():
        return Node, 'Медианный Фильтр', 'camera'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
