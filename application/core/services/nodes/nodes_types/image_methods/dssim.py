

import customtkinter as ctk
import os
from application.core.events import Event
from application.core.services.nodes.node import INode
from tkinter.filedialog import askdirectory
from matplotlib import cm
from PIL import Image
from skimage.metrics import structural_similarity as ssim
import numpy as np


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('A', self.palette['CAMERA_SHOT'])
        self.add_enter_socket('B', self.palette['CAMERA_SHOT'])

        self.add_output_socket('', self.palette['NUM'])

        self.load_data = kwargs
        self.strong_control = False


    def execute(self):
        arguments = self.get_func_inputs()

        image_a = arguments['A'].copy()
        image_b = arguments['B'].copy()

        image_a = image_a / np.max(image_a)
        image_b = image_b / np.max(image_b)

        metric = ssim(image_a, image_b, data_range=image_a.max() - image_a.min(),)

        print(metric)

        metric = (1 - metric) /2

        self.output_sockets[''].set_value(metric)





        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'DSSIM(A, B)', 'Metric'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
