from application.core.events import Event
from application.core.services.nodes.node import INode
import customtkinter as ctk
import time


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Вектор', self.palette['vector1d'])

        self.add_enter_socket('Элемент', self.palette['ANY'])

        self.add_output_socket('Вектор', self.palette['vector1d'])

    def execute(self):
        arguments = self.get_func_inputs()

        name = arguments['Вектор']

        vector = self.editor.vectors[name]

        vector = vector.copy()


        element = arguments['Элемент']

        vector.append(element)

        self.output_sockets['Вектор'].set_value(vector)
        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Append', 'Container'

    @staticmethod
    def possible_to_create():
        return True

    def prepare_save_spec(self):
        return __file__, self.x, self.y, {}, self.special_id, self.with_signals
