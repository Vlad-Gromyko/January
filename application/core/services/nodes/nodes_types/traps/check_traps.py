import numpy as np

from application.core.events import Event
from application.core.services.nodes.node import INode
import customtkinter as ctk
import time
from application.core.utility.mask import Mask


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Снимок', self.palette['CAMERA_SHOT'])
        self.add_enter_socket('Вектор X', self.palette['vector1d'])
        self.add_enter_socket('Вектор Y', self.palette['vector1d'])
        self.add_enter_socket('Область', self.palette['NUM'])
        self.add_enter_socket('Целевое Распределение', self.palette['vector1d'])

        self.add_output_socket('Вектор I', self.palette['vector1d'])
        self.add_output_socket('Uniformity', self.palette['NUM'])
        self.add_output_socket('D', self.palette['NUM'])
        self.add_output_socket('srez', self.palette['CAMERA_SHOT'])

        self.load_data = kwargs

    def execute(self):
        arguments = self.get_func_inputs()

        shot = arguments['Снимок']
        x_list = arguments['Вектор X']
        y_list = arguments['Вектор Y']
        search_radius = int(arguments['Область'])

        design = np.asarray(arguments['Целевое Распределение'])

        intensities = []

        for i in range(len(x_list)):
            x = x_list[i]
            y = y_list[i]

            mask = np.zeros_like(shot)
            mask[x - search_radius: x + search_radius, y - search_radius: y + search_radius] = 1

            intensities.append(np.max(shot * mask))
            self.output_sockets['srez'].set_value(shot * mask)

        intensities = np.asarray(intensities)
        intensities = intensities / np.max(intensities)
        d = np.sum(np.abs(intensities - design))
        intensities = list(intensities)

        uniformity = 1 - (np.max(intensities / design) - np.min(intensities / design)) / (np.max(intensities / design) + np.min(intensities / design))

        intensities = list(intensities)

        self.output_sockets['Вектор I'].set_value(intensities)
        self.output_sockets['Uniformity'].set_value(uniformity)
        self.output_sockets['D'].set_value(d)

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Проверить ловушки', 'traps'

    @staticmethod
    def possible_to_create():
        return True

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
