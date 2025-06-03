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
        self.add_enter_socket('Разброс', self.palette['NUM'])

        self.add_output_socket('Сигнал', self.palette['SIGNAL'])
        self.add_output_socket('Голограмма', self.palette['HOLOGRAM'])
        self.add_output_socket('X', self.palette['NUM'])
        self.add_output_socket('Y', self.palette['NUM'])
        self.add_output_socket('Коррекция', self.palette['HOLOGRAM'])

        self.load_data = kwargs

    def execute(self):
        arguments = self.get_func_inputs()

        shot = arguments['Снимок']

        y, x = np.shape(shot)
        x = np.linspace(-x / 2, x / 2, x)
        y = np.linspace(-y / 2, y / 2, y)

        x, y = np.meshgrid(x, y)

        x_coord_start = float(np.sum(shot * x) / np.sum(shot))
        y_coord_start = float(np.sum(shot * y) / np.sum(shot))

        print(x_coord_start, y_coord_start)

        self.event_bus.raise_event(Event('Calculate Zernike One', {'number': 1, 'amplitude': arguments['Разброс']}))
        holo1 = self.event_bus.get_field('Last Zernike Mask')

        self.event_bus.raise_event(Event('Calculate Zernike One', {'number': 2, 'amplitude': arguments['Разброс']}))
        holo2 = self.event_bus.get_field('Last Zernike Mask')

        self.output_sockets['Голограмма'].set_value(holo1 + holo2)
        self.output_sockets['Сигнал'].set_value(True)

        arguments = self.get_func_inputs()
        shot = arguments['Снимок']

        y, x = np.shape(shot)
        x = np.linspace(-x / 2, x / 2, x)
        y = np.linspace(-y / 2, y / 2, y)

        x, y = np.meshgrid(x, y)

        x_coord_end = float(np.sum(shot * x) / np.sum(shot))
        y_coord_end = float(np.sum(shot * y) / np.sum(shot))

        print(x_coord_end, y_coord_end)

        result_x = float(arguments['Разброс'] / (x_coord_start - x_coord_end) * x_coord_start)
        result_y = float(arguments['Разброс'] / (y_coord_start - y_coord_end) * y_coord_start)

        self.output_sockets['X'].set_value(result_x)
        self.output_sockets['Y'].set_value(result_y)

        self.event_bus.raise_event(Event('Calculate Zernike One', {'number': 1, 'amplitude': result_y}))
        holo1 = self.event_bus.get_field('Last Zernike Mask')

        self.event_bus.raise_event(Event('Calculate Zernike One', {'number': 2, 'amplitude': result_x}))
        holo2 = self.event_bus.get_field('Last Zernike Mask')

        self.output_sockets['Коррекция'].set_value(holo1 + holo2)

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Коррекция центра', 'algo'

    @staticmethod
    def possible_to_create():
        return True

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
