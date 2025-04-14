from application.core.events import Event
from application.core.services.nodes.node import INode
import customtkinter as ctk
import time


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Вектор', self.palette['vector2d'])
        self.add_enter_socket('Строка', self.palette['NUM'])
        self.add_enter_socket('Столбец', self.palette['NUM'])


        self.add_output_socket('Элемент', self.palette['ANY'])
        self.load_data = kwargs

        self.strong_control = True
    def execute(self):
        arguments = self.get_func_inputs()

        vector = arguments['Вектор']
        vector = self.editor.matrices[vector].copy()
        num1 = arguments['Строка']
        num2 = arguments['Столбец']

        self.output_sockets[''].set_value(vector[num1][num2])

    @staticmethod
    def create_info():
        return Node, 'Get 2', 'Container'

    @staticmethod
    def possible_to_create():
        return True

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
