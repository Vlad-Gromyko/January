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
        self.add_enter_socket('T', self.palette['NUM'])
        self.add_enter_socket('Стагнация', self.palette['NUM'])
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


        self.u_history = []
        self.weights_history = []
        self.intensities_history = []
        self.gradient_history = []

        self.best_weights = []
        self.best_uniformity = []
        self.best_intensities = []

        self.solution = []

        self.design = []

        self.start_thresh = 1
        self.stag = 0
        self.momentum = 1

    def iteration(self, weights):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"The time is {now}")

        self.output_sockets['Решение'].set_value(list(weights))
        print(weights)
        self.output_sockets['Метрика'].set_value(True)

        arguments = self.get_func_inputs()

        values = np.asarray(arguments['Интенсивности'])

        u = self.uniformity(values / self.design)

        if (len(self.best_uniformity) == 0) or (u > self.best_uniformity[-1]):
            self.best_uniformity.append(u)
            self.best_weights.append(weights)

            print('best')
            self.stag = 0
        else:
            self.stag += 1
            if self.stag == 30:
                self.stag = 0
                self.start_thresh *= 3
                print('stagnation')

        self.weights_history.append(weights)
        self.intensities_history.append(values)
        self.u_history.append(u)

    def execute(self):

        self.u_history = []
        self.weights_history = []
        self.intensities_history = []
        self.gradient_history = []

        self.best_weights = []
        self.best_uniformity = []
        self.best_intensities = []

        self.solution = []

        self.design = []

        self.start_thresh = 1
        self.stag = 0

        arguments = self.get_func_inputs()
        velocity = arguments['Скорость']
        thresh = arguments['T']
        momentum = arguments['Момент']

        self.start_thresh = thresh
        self.design = np.asarray(arguments['Целевое Распределение'])

        weights = arguments['Решение']
        self.iteration(weights)


        for k in range(0, int(arguments['Число Итераций'])):
            self.output_sockets['Индекс'].set_value(k)
            values = self.intensities_history[-1]


            thresh = self.start_thresh if self.stag == 0 else thresh * 2

            print(velocity / thresh)

            momentum_weight = 0
            if len(self.weights_history) > 2:
                momentum_weight = momentum * (self.weights_history[-1] - self.weights_history[-2])

            weights = self.best_weights[-1]
            weights = weights + velocity * (self.design / np.max(self.design) - values)  / thresh - momentum_weight

            self.iteration(weights)

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def uniformity(values):
        return 1 - (np.max(values) - np.min(values)) / (np.max(values) + np.min(values))

    @staticmethod
    def create_info():
        return Node, 'Декабрь', 'gradient'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
