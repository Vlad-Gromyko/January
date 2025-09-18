
from application.core.events import Event
from application.core.services.nodes.node import INode
import customtkinter as ctk
import time
from functools import reduce


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Вектор A', self.palette['vector1d'])
        self.add_enter_socket('Вектор B', self.palette['vector1d'])

        self.add_output_socket('', self.palette['vector1d'])

        self.load_data = kwargs

        self.strong_control = True
    def execute(self):

        arguments = self.get_func_inputs()

        vector_a = arguments['Вектор A'].copy()
        vector_b = arguments['Вектор B'].copy()

        vector_a.extend(vector_b)


        self.output_sockets[''].set_value(vector_a)

        print('aaaa')


        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'A.extend(B)', 'Container'

    @staticmethod
    def possible_to_create():
        return True

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
