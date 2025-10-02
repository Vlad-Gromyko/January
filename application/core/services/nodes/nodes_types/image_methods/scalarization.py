import customtkinter as ctk
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
import matplotlib.pyplot as plt

from application.core.services.nodes.node import INode
from application.core.utility.mask import Mask


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('', self.palette['vector1d'])
        self.add_enter_socket('M0', self.palette['SIGNAL'], )
        self.add_enter_socket('M', self.palette['SIGNAL'], )

        self.add_output_socket('', self.palette['NUM'],)

        self.load_data = kwargs

        self.start_metrics = []

        self.widget_width = 400
        self.widget_height = 600
        frame_widgets = ctk.CTkFrame(self.canvas, width=self.widget_width, height=self.widget_height)
        self.frame_IDs['widgets'] = self.canvas.create_window(self.x, self.y, window=frame_widgets,
                                                              anchor=ctk.NW, width=self.widget_width,
                                                              height=self.widget_height)

        self.metric_methods = ['Аддитивная', 'Мультипликативная', 'Показательная', 'Энтропийная']

        self.combobox = ctk.CTkComboBox(frame_widgets, values=self.metric_methods)
        self.combobox.set('Аддитивная')
        self.combobox.grid(row=0, column=0, padx=10, pady=10)

        self.metrics = ['MDS', 'Сигма', 'DDSIM + 1', 'Компактность']

        self.entries = {}

        for counter, item in enumerate(self.metrics):
            ctk.CTkLabel(frame_widgets, text=item).grid(row=counter + 1, column=0, padx=10, pady=10)
            self.entries[item] = ctk.CTkEntry(frame_widgets, width=200)
            self.entries[item].insert(0, '1')
            self.entries[item].grid(row=counter + 1, column=1, padx=10, pady=10)

    def execute(self):
        arguments = self.get_func_inputs()

        value = np.asarray(arguments[''])

        if arguments['M0'] is not None:
            self.start_metrics = value

        value = value / self.start_metrics

        weights = np.ones_like(value)

        for counter, item in enumerate(self.metrics):
            weights[counter] = float(self.entries[item].get())

        if self.combobox.get() == 'Аддитивная':
            self.output_sockets[''].set_value(np.sum(value * weights))
        elif self.combobox.get() == 'Мультипликативная':
            self.output_sockets[''].set_value(np.prod(value ** weights))
        elif self.combobox.get() == 'Показательная':
            self.output_sockets[''].set_value(np.sum(1 - np.exp(-value * weights)))
        elif self.combobox.get() == 'Энтропийная':
            self.output_sockets[''].set_value(np.sum(weights * value ** weights))

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Скаляризация', 'Plots'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
