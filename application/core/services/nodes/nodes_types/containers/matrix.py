import numpy as np

from application.core.events import Event
from application.core.services.nodes.node import INode
import customtkinter as ctk
import time


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Число Строк', self.palette['NUM'])
        self.add_enter_socket('Число Столбцов', self.palette['NUM'])
        self.add_enter_socket('Элемент', self.palette['ANY'])

        self.add_output_socket('Матрица', self.palette['vector2d'])
        self.load_data = kwargs
    def execute(self):
        arguments = self.get_func_inputs()

        num1 = int(arguments['Число Строк'])
        num2 = int(arguments['Число Столбцов'])
        element = arguments['Элемент']

        vector = np.ones((num1, num2)) * element

        self.output_sockets['Матрица'].set_value(vector)

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Матрица', 'Container'

    @staticmethod
    def possible_to_create():
        return True

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
