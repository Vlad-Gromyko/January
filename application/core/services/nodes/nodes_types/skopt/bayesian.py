import numpy
import numpy as np
import customtkinter as ctk
from application.core.services.nodes.node import INode

from skopt import gp_minimize
from skopt.space import Real
from skopt import Optimizer


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Обучить', self.palette['SIGNAL'])
        self.add_enter_socket('Прогнозировать', self.palette['SIGNAL'])
        self.add_enter_socket('Решение', self.palette['vector1d'])
        self.add_enter_socket('Метрика', self.palette['NUM'])

        self.add_enter_socket('MAX', self.palette['NUM'])
        self.add_enter_socket('MIN', self.palette['NUM'])

        self.add_output_socket('', self.palette['SIGNAL'])
        self.add_output_socket('Прогноз', self.palette['vector1d'])

        self.load_data = kwargs
        self.strong_control = False

        self.widget_width = 200
        self.widget_height = 200
        frame_widgets = ctk.CTkFrame(self.canvas, width=self.widget_width, height=self.widget_height)
        self.frame_IDs['widgets'] = self.canvas.create_window(self.x, self.y, window=frame_widgets,
                                                              anchor=ctk.NW, width=self.widget_width,
                                                              height=self.widget_height)

        ctk.CTkButton(frame_widgets, text="Обнулить Оптимизатор", command=self.reborn_optimizer).grid(row=0, column=0,
                                                                                                      padx=5, pady=5)

        estimators = ['GP', 'RF', 'ET', 'GBRT']

        self.combobox = ctk.CTkComboBox(frame_widgets, values=estimators)
        self.combobox.set('GP')
        self.combobox.grid(row=1, column=0, padx=5, pady=5)

        acq = ['LCB', 'EI', 'PI', 'gp_hedge', 'EIps', 'PIps']

        self.combobox_acq = ctk.CTkComboBox(frame_widgets, values=acq)
        self.combobox_acq.set('EI')
        self.combobox_acq.grid(row=2, column=0, padx=5, pady=5)

        self.label_errors = ctk.CTkLabel(frame_widgets, text='Отброшенных значений: 0')
        self.label_errors.grid(row=3, column=0, padx=5, pady=5)

        self.optimizer = None

    def reborn_optimizer(self):
        arguments = self.get_func_inputs()

        space = [Real(arguments['MIN'], arguments['MAX'], name=f'x{i}') for i in range(len(arguments['Решение']))]

        estimator = self.combobox.get()
        acq = self.combobox_acq.get()
        self.optimizer = Optimizer(space, base_estimator=estimator, acq_func=acq, n_initial_points=0)
        self.label_errors.configure(text=f'Отброшенных значений: 0')

    def teach(self):
        try:
            print('Обучение')
            arguments = self.get_func_inputs()
            self.optimizer.tell(arguments['Решение'], arguments['Метрика'])
        except ValueError:
            pass

    def ask(self):
        x = self.optimizer.ask()

        self.output_sockets['Прогноз'].set_value(x)
        self.output_sockets[''].set_value(True)

        arguments = self.get_func_inputs()

        try:
            self.optimizer.tell(x, arguments['Метрика'])
        except ValueError:
            pass

    def execute(self):
        arguments = self.get_func_inputs()

        if self.optimizer is None:
            self.reborn_optimizer()

        if arguments['Обучить'] is not None:
            self.teach()
        elif arguments['Прогнозировать'] is not None:
            self.ask()

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Байесовская оптимизация', 'strategy'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
