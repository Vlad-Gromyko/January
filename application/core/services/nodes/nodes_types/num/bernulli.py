import numpy as np

from application.core.events import Event
from application.core.services.nodes.node import INode
import customtkinter as ctk
import time
import random

class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Длина', self.palette['NUM'])

        self.add_enter_socket('Амплитуда', self.palette['NUM'])

        self.add_output_socket('', self.palette['vector1d'])

        self.load_data = kwargs
    def execute(self):
        arguments = self.get_func_inputs()

        num = int(arguments['Длина'])
        amp = arguments['Амплитуда']

        result = [amp if np.random.rand() < 0.5 else -1 * amp for i in range(num)]

        self.output_sockets[''].set_value(result)

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Бернулли Вектор', 'math'

    @staticmethod
    def possible_to_create():
        return True

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
