
from application.core.events import Event
from application.core.services.nodes.node import INode
import customtkinter as ctk
import time
from functools import reduce

from application.core.utility.fast_zernike import zernike_by_number
import numpy as np

import matplotlib.pyplot as plt

class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Начало', self.palette['NUM'])
        self.add_enter_socket('Длина', self.palette['NUM'])

        self.add_output_socket('Базис', self.palette['vector1d'])

        self.load_data = kwargs

        self.strong_control = True

        self.processed = {}

        self.rho = None
        self.phi = None

        self.widget_width = 200
        self.widget_height = 40
        frame_widgets = ctk.CTkFrame(self.canvas, width=self.widget_width, height=self.widget_height)
        self.frame_IDs['widgets'] = self.canvas.create_window(self.x, self.y, window=frame_widgets,
                                                              anchor=ctk.NW, width=self.widget_width,
                                                              height=self.widget_height)
        self.check_var = ctk.StringVar(value="off")
        self.checkbox = ctk.CTkCheckBox(frame_widgets, text="floor",
                                        variable=self.check_var, onvalue="on", offvalue="off")
        self.checkbox.grid(row=0, column=0, padx=5, pady=5)

    def execute(self):
        timer = time.time()
        arguments = self.get_func_inputs()

        start = arguments['Начало']
        length = arguments['Длина']

        if self.phi is None:

            slm_width = self.event_bus.get_field('slm width')
            slm_height = self.event_bus.get_field('slm height')

            radius_y = 1

            radius_x = radius_y / slm_height * slm_width

            _x = np.linspace(-radius_x, radius_x, slm_width)
            _y = np.linspace(-radius_y, radius_y, slm_height)

            _x, _y = np.meshgrid(_x, _y)

            self.rho = np.sqrt(_x ** 2 + _y ** 2)

            self.phi = np.arctan2(_y, _x)

            self.phi = np.flip(self.phi, axis=0)

        result = []

        for i in range(int(start), int(start+length)):
            if str(i) not in self.processed.keys():
                self.processed[str(i)] = zernike_by_number(i, self.rho, self.phi)

            mask = self.processed[str(i)]

            result.append(mask)
            print('Zernike', i, 'done',)


        self.output_sockets['Базис'].set_value(result)



        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Цернике', 'Базисы'

    @staticmethod
    def possible_to_create():
        return True

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
