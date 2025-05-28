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

        self.load_data = kwargs


    def execute(self):
        arguments = self.get_func_inputs()

        a = arguments['A']
        b = arguments['B']

        a_len = 1
        b_len = 1

        result_a = a
        result_b = b

        plus = 0
        minus = 0
        mul = 0

        if hasattr(a, '__len__') and not isinstance(a, Mask):
            a_len = len(a)
        if hasattr(b, '__len__') and not isinstance(b, Mask):
            b_len = len(b)

        if a_len == 1 and b_len == 1:
            plus = result_a + result_b
            minus = result_a - result_b
            mul = result_a * result_b
        elif a_len == 1 and b_len >1:
            result_a = [a for i in range(b_len)]
            plus = []
            minus = []
            mul = []
            for i in range(b_len):
                plus.append(result_a[i] + result_b[i])
                minus.append(result_a[i] - result_b[i])
                mul.append(result_a[i] * result_b[i])
        elif a_len > 1 and b_len == 1:
            result_b = [b for i in range(a_len)]
            plus = []
            minus = []
            mul = []
            for i in range(a_len):
                plus.append(result_a[i] + result_b[i])
                minus.append(result_a[i] - result_b[i])
                mul.append(result_a[i] * result_b[i])
        else:
            for i in range(a_len):
                plus = []
                minus = []
                mul = []
                plus.append(result_a[i] + result_b[i])
                minus.append(result_a[i] - result_b[i])
                mul.append(result_a[i] * result_b[i])


        self.output_sockets['+'].set_value(plus)
        self.output_sockets['-'].set_value(minus)
        self.output_sockets['*'].set_value(mul)


        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'A ~ B', 'math'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals