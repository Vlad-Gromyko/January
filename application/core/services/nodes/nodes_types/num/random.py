import numpy as np

from application.core.events import Event
from application.core.services.nodes.node import INode
import customtkinter as ctk
import time


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Max', self.palette['NUM'])
        self.add_enter_socket('Min', self.palette['NUM'])

        self.add_output_socket('int', self.palette['NUM'])
        self.add_output_socket('float', self.palette['NUM'])


    def execute(self):
        arguments = self.get_func_inputs()

        num1 = arguments['От']
        num2 = arguments['До']


        value = np.random.uniform(num1, num2)

        self.output_sockets['int'].set_value(int(value))
        self.output_sockets['float'].set_value(value)



        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Ловушка', 'traps'

    @staticmethod
    def possible_to_create():
        return True

    def prepare_save_spec(self):
        return __file__, self.x, self.y, {}, self.special_id, self.with_signals
