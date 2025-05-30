import numpy as np

from application.core.events import Event
from application.core.services.nodes.node import INode
import customtkinter as ctk
import time


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Номер', self.palette['NUM'])

        self.add_output_socket('X', self.palette['NUM'])
        self.add_output_socket('Y', self.palette['NUM'])
        self.add_output_socket('Z', self.palette['NUM'])
        self.add_output_socket('W', self.palette['NUM'])
        self.add_output_socket('[]', self.palette['vector1d'])
        self.load_data = kwargs


    def execute(self):
        arguments = self.get_func_inputs()

        num = arguments['Номер']

        traps = self.event_bus.get_field('Traps')

        trap = traps[int(num)]

        self.output_sockets['X'].set_value(trap[0])
        self.output_sockets['Y'].set_value(trap[1])
        self.output_sockets['Z'].set_value(trap[2])
        self.output_sockets['W'].set_value(trap[3])
        self.output_sockets['[]'].set_value(trap)

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Ловушка', 'traps'

    @staticmethod
    def possible_to_create():
        return True

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
