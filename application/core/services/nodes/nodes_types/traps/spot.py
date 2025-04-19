import numpy as np

from application.core.events import Event
from application.core.services.nodes.node import INode
import customtkinter as ctk
import time


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Снимок', self.palette['CAMERA_SHOT'])

        self.add_output_socket('X', self.palette['NUM'])
        self.add_output_socket('Y', self.palette['NUM'])
        self.load_data = kwargs

    def execute(self):
        arguments = self.get_func_inputs()

        shot = np.asarray(arguments['Снимок'])

        y, x = np.shape(shot)

        x = np.linspace(0, x, x)
        y = np.linspace(0, y, y)

        x, y = np.meshgrid(x, y)

        x_coord = int(np.sum(shot * x) / np.sum(shot))
        y_coord = int(np.sum(shot * y) / np.sum(shot))

        self.output_sockets['X'].set_value(x_coord)
        self.output_sockets['Y'].set_value(y_coord)

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Координаты ловушки', 'camera'

    @staticmethod
    def possible_to_create():
        return True

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
