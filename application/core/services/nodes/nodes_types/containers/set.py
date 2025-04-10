from application.core.events import Event
from application.core.services.nodes.node import INode
import customtkinter as ctk
import time


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Вектор', self.palette['vector1d'])
        self.add_enter_socket('Номер', self.palette['NUM'])
        self.add_enter_socket('Элемент', self.palette['ANY'])

        self.add_output_socket('Вектор', self.palette['vector1d'])



    def execute(self):
        arguments = self.get_func_inputs()

        vector = arguments['Вектор'].copy()

        num = arguments['Номер']
        element = arguments['Элемент']

        vector[num] = element

        self.output_sockets['Вектор'].set_value(vector)

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Set', 'Container'

    @staticmethod
    def possible_to_create():
        return True

    def prepare_save_spec(self):
        return __file__, self.x, self.y, {}, self.special_id, self.with_signals
