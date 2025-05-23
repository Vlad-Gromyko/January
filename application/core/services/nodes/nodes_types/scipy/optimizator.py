import numpy
import numpy as np
import customtkinter as ctk
from application.core.services.nodes.node import INode

from scipy.optimize import minimize


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Число Итераций', self.palette['NUM'])
        self.add_enter_socket('Решение', self.palette['vector1d'])
        self.add_enter_socket('Метрика', self.palette['NUM'])


        self.add_output_socket('Индекс', self.palette['NUM'])
        self.add_output_socket('Целевая Функция', self.palette['SIGNAL'])
        self.add_output_socket('Решение', self.palette['vector1d'])

        self.add_output_socket('После Итерации', self.palette['SIGNAL'])

        self.load_data = kwargs
        self.strong_control = True



        frame_widgets = ctk.CTkFrame(self.canvas, width=self.widget_width, height=self.widget_height)
        self.frame_IDs['widgets'] = self.canvas.create_window(self.x, self.y, window=frame_widgets,
                                                              anchor=ctk.NW, width=self.widget_width,
                                                              height=self.widget_height)

        values = ['Nelder-Mead',
                  'Powell',
                  'CG',
                  'BFGS',
                  'Newton-CG',
                  'L-BFGS-B',
                  'TNC',
                  'COBYLA',
                  'COBYQA',
                  'SLSQP',
                  'trust-constr',
                  'dogleg',
                  'trust-ncg',
                  'trust-krylov',
                  'trust-exact']


        self.combo = ctk.CTkComboBox(frame_widgets, values=values)
        self.combo.set('L-BFGS-B')

        self.combo.pack()

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
        self.counter = 0

        result = minimize(self.explore_func, arguments['Решение'], method=self.combo.get(), options={'maxiter': int(arguments['Число Итераций'])})
        self.output_sockets['Решение'].set_value(list(result.x))


        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Оптимизатор', 'strategy'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
