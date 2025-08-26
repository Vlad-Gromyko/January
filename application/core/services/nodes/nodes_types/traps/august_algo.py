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
        self.add_enter_socket('Lambda', self.palette['NUM'])
        self.add_enter_socket('Beta', self.palette['NUM'])
        self.add_enter_socket('P', self.palette['NUM'])

        self.add_enter_socket('Решение', self.palette['vector1d'])

        self.add_enter_socket('Интенсивности', self.palette['vector1d'])

        self.add_output_socket('Индекс', self.palette['NUM'])
        self.add_output_socket('Метрика', self.palette['SIGNAL'])

        self.add_output_socket('Решение', self.palette['vector1d'])

        self.add_output_socket('После Итерации', self.palette['SIGNAL'])

        self.previous = None

        self.load_data = kwargs
        self.strong_control = True

        self.widget_width = 200
        self.widget_height = 40
        frame_widgets = ctk.CTkFrame(self.canvas, width=self.widget_width, height=self.widget_height)
        self.frame_IDs['widgets'] = self.canvas.create_window(self.x, self.y, window=frame_widgets,
                                                              anchor=ctk.NW, width=self.widget_width,
                                                              height=self.widget_height)
        self.check_var = ctk.StringVar(value="on")
        self.checkbox = ctk.CTkCheckBox(frame_widgets, text="Best",
                                        variable=self.check_var, onvalue="on", offvalue="off")
        self.checkbox.grid(row=0, column=0, padx=5, pady=5)

        self.u_history = []
        self.weights_history = []
        self.intensities_history = []
        self.gradient_history = []

        self.best_weights = []
        self.best_uniformity = []
        self.best_intensities = []

        self.solution = []

        self.design = []


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

        arguments = self.get_func_inputs()

        self.design = np.asarray(arguments['Целевое Распределение'])

        weights = arguments['Решение']
        self.iteration(weights)

        decay = arguments['Lambda']
        beta = arguments['Beta']
        p = arguments['P']

        for k in range(0, int(arguments['Число Итераций'])):
            self.output_sockets['Индекс'].set_value(k)
            values = self.intensities_history[-1]
            if self.checkbox.get() == 'on':
                weights = self.best_weights[-1]
            else:
                weights = self.weights_history[-1]

            gradient = (self.design / np.max(self.design) - values)
            gradient = gradient / np.linalg.norm(gradient)

            decay_operator = decay / len(weights)
            random_operator = np.random.uniform(-1, 1, len(weights))
            random_operator = np.linalg.norm(random_operator) * beta
            weights = weights + decay_operator * (gradient + random_operator) * (1 - self.u_history[-1] ** p) ** (1/p)

            self.iteration(weights)

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def uniformity(values):
        return 1 - (np.max(values) - np.min(values)) / (np.max(values) + np.min(values))

    @staticmethod
    def create_info():
        return Node, 'Новый Август', 'gradient'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
