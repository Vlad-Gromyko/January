from application.core.events import Event
from application.core.services.nodes.node import INode
import customtkinter as ctk
import time


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Вектор', self.palette['vector1d'])
        self.add_enter_socket('Строка', self.palette['NUM'])
        self.add_enter_socket('Столбец', self.palette['NUM'])
        self.add_enter_socket('Элемент', self.palette['ANY'])

        self.add_output_socket('Вектор', self.palette['vector1d'])



    def execute(self):
        arguments = self.get_func_inputs()

        name = arguments['Вектор']
        vector = self.editor.matrices[name].copy()
        num1 = arguments['Строка']
        num2 = arguments['Столбец']
        element = arguments['Элемент']

        vector[num1][num2] = element

        self.event_bus.raise_event(
            Event('Vector Updated', {'name': name, 'value': vector, 'tab': self.editor}))

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Set 2', 'Container'

    @staticmethod
    def possible_to_create():
        return True

    def prepare_save_spec(self):
        return __file__, self.x, self.y, {}, self.special_id, self.with_signals
