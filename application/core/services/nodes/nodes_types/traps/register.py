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

        self.add_enter_socket('Ловушки', self.palette['vector1d'])
        self.add_enter_socket('X', self.palette['NUM'])
        self.add_enter_socket('Y', self.palette['NUM'])

        self.add_output_socket('', self.palette['SIGNAL'])
        self.add_output_socket('Голограмма', self.palette['HOLOGRAM'])

        self.add_output_socket('Вектор X', self.palette['vector1d'])
        self.add_output_socket('Вектор Y', self.palette['vector1d'])
        self.load_data = kwargs

    def execute(self):
        arguments = self.get_func_inputs()

        traps = arguments['Ловушки']

        x = []
        y = []

        for item in traps:
            x.append(item[0])
            y.append(item[1])

        width = int(self.event_bus.get_field('slm width'))
        height = int(self.event_bus.get_field('slm height'))
        pixel = self.event_bus.get_field('slm pixel')

        focus = self.event_bus.get_field('optics focus')
        wave = self.event_bus.get_field('laser wavelength')

        x_mesh = np.linspace(-width * pixel / 2, width * pixel / 2, width)
        y_mesh = np.linspace(-height * pixel / 2, height * pixel / 2, height)

        x_mesh, y_mesh = np.meshgrid(x_mesh, y_mesh)
        x_mesh, y_mesh = x_mesh * 2 * np.pi / wave / focus, y_mesh * 2 * np.pi / wave / focus

        x_result = []
        y_result = []

        for i in range(len(x)):
            holo = (x_mesh * x[i] + y_mesh * y[i]) % (2 * np.pi)
            holo = Mask(holo)
            self.output_sockets['Голограмма'].set_value(holo)
            self.output_sockets[''].set_value(True)
            arguments = self.get_func_inputs()

            x_spot = arguments['X']
            y_spot = arguments['Y']

            x_result.append(x_spot)
            y_result.append(y_spot)

        self.output_sockets['Вектор X'].set_value(x_result)
        self.output_sockets['Вектор Y'].set_value(y_result)


        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Регистрация Ловушек', 'traps'

    @staticmethod
    def possible_to_create():
        return True

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
