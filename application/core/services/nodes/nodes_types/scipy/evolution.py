import numpy
import numpy as np
import customtkinter as ctk
from application.core.services.nodes.node import INode

from scipy.optimize import minimize, differential_evolution


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Число Итераций', self.palette['NUM'])
        self.add_enter_socket('Разброс', self.palette['NUM'])
        self.add_enter_socket('Решение', self.palette['vector1d'])
        self.add_enter_socket('Метрика', self.palette['NUM'])

        self.add_output_socket('Индекс', self.palette['NUM'])
        self.add_output_socket('Целевая Функция', self.palette['SIGNAL'])
        self.add_output_socket('Решение', self.palette['vector1d'])

        self.add_output_socket('После Итерации', self.palette['SIGNAL'])

        self.load_data = kwargs
        self.strong_control = True

        self.counter = 0

    def explore_func(self, solution):
        self.output_sockets['Индекс'].set_value(self.counter)
        self.output_sockets['Решение'].set_value(list(solution))
        self.output_sockets['Целевая Функция'].set_value(True)

        self.counter += 1
        arguments = self.get_func_inputs()

        return arguments['Метрика']

    def execute(self):
        arguments = self.get_func_inputs()
        n = len(arguments['Решение'])

        edge = arguments['Разброс']

        self.counter = 0

        bounds = [(- edge, edge) for i in range(n)]

        result = differential_evolution(self.explore_func, bounds, maxiter=10)
        self.output_sockets['Решение'].set_value(list(result.x))

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Эволюция', 'strategy'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
