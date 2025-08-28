import numpy
import numpy as np
import customtkinter as ctk
from application.core.services.nodes.node import INode
import datetime


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Число Итераций', self.palette['NUM'])
        self.add_enter_socket('Целевое Распределение', self.palette['vector1d'])
        self.add_enter_socket('Скорость', self.palette['NUM'])
        self.add_enter_socket('Степень U', self.palette['NUM'])
        self.add_enter_socket('Разложение', self.palette['NUM'])

        self.add_enter_socket('Момент', self.palette['NUM'])
        self.add_enter_socket('Решение', self.palette['vector1d'])

        self.add_enter_socket('Интенсивности', self.palette['vector1d'])

        self.add_output_socket('Индекс', self.palette['NUM'])
        self.add_output_socket('Метрика', self.palette['SIGNAL'])

        self.add_output_socket('Решение', self.palette['vector1d'])


        self.add_output_socket('После Итерации', self.palette['SIGNAL'])




        self.previous = None

        self.load_data = kwargs
        self.strong_control = True






        self.design = []

        self.intensities_history = []
        self.u_history = []

        self.momentum = 1
        self.velocity = 1
        self.power = 1
        self.decay = 1
        self.weights_history = []


    def iteration(self, weights):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"The time is {now}")

        self.output_sockets['Решение'].set_value(list(weights))

        self.output_sockets['Метрика'].set_value(True)

        arguments = self.get_func_inputs()

        values = np.asarray(arguments['Интенсивности'])

        u = self.uniformity(values / self.design)
        self.u_history.append(u)

        self.intensities_history.append(values)
        self.weights_history.append(weights)


    def execute(self):

        self.intensities_history = []
        self.u_history = []
        self.design = []

        self.weights_history = []

        arguments = self.get_func_inputs()
        self.velocity = arguments['Скорость']

        self.power = arguments['Степень U']
        self.decay = arguments['Разложение']

        self.momentum = arguments['Момент']

        self.design = np.asarray(arguments['Целевое Распределение'])

        weights = arguments['Решение']
        self.iteration(weights)


        for k in range(0, int(arguments['Число Итераций'])):
            self.output_sockets['Индекс'].set_value(k)
            values = self.intensities_history[-1]



            gradient = (self.design / np.max(self.design) - values)
            print(gradient)

            weights = weights + self.velocity * gradient * np.exp(-k * self.decay)
            if len(self.weights_history) > 1:

                weights = weights - self.momentum * (weights - self.weights_history[-1])

            self.iteration(weights)

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def uniformity(values):
        return 1 - (np.max(values) - np.min(values)) / (np.max(values) + np.min(values))

    @staticmethod
    def create_info():
        return Node, 'True Old', 'gradient'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
