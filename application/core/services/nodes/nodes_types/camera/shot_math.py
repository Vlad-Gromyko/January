import customtkinter as ctk
import numpy as np

from application.core.services.nodes.node import INode
from application.core.utility.mask import Mask


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('A', self.palette['ANY'])
        self.add_enter_socket('B', self.palette['ANY'])

        self.add_output_socket('+', self.palette['ANY'])
        self.add_output_socket('-', self.palette['ANY'])
        self.add_output_socket('*', self.palette['ANY'])
        self.add_output_socket('/', self.palette['ANY'])

        self.load_data = kwargs
        self.widget_width = 120
        self.widget_height = 25
        frame_widgets = ctk.CTkFrame(self.canvas, width=self.widget_width, height=self.widget_height)
        self.frame_IDs['widgets'] = self.canvas.create_window(self.x, self.y, window=frame_widgets,
                                                              anchor=ctk.NW, width=self.widget_width,
                                                              height=self.widget_height)

        self.num_label = ctk.CTkLabel(frame_widgets, text='', anchor=ctk.NW)
        self.num_label.grid(padx=5, pady=5)

    def execute(self):
        arguments = self.get_func_inputs()

        a = arguments['A']
        b = arguments['B']

        self.output_sockets['+'].set_value(a + b)
        self.output_sockets['-'].set_value(np.abs(a - b))
        self.output_sockets['*'].set_value(a * b)
        self.output_sockets['/'].set_value(a / b)

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Shot A ~ Shot B', 'camera'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
