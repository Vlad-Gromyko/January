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
        self.add_enter_socket('Добавить', self.palette['SIGNAL'], )
        self.add_enter_socket('Очистить', self.palette['SIGNAL'], )

        self.load_data = kwargs
        self.widget_width = 500
        self.widget_height = 500
        frame_widgets = ctk.CTkFrame(self.canvas, width=self.widget_width, height=self.widget_height)
        self.frame_IDs['widgets'] = self.canvas.create_window(self.x, self.y, window=frame_widgets,
                                                              anchor=ctk.NW, width=self.widget_width,
                                                              height=self.widget_height)

        self.fig = Figure(figsize=(7, 7), dpi=100)

        self.ax = self.fig.add_subplot(111)

        self.plot_canvas = FigureCanvasTkAgg(self.fig,
                                             master=frame_widgets)
        self.plot_canvas.draw()

        self.plot_canvas.get_tk_widget().pack()

        self.metrics = []
        self.start_metrics = []

    def draw(self):

        self.ax.cla()
        names = ['Метрика', 'MDS', 'Sigma', 'DSSIM']

        transposed_data = list(zip(*self.metrics))

        normalized_data = []
        for line in transposed_data:
            first_value = line[0]

            normalized_line = [x / first_value for x in line]
            normalized_data.append(normalized_line)

        for i, (data_column, name) in enumerate(zip(normalized_data, names)):
            self.ax.plot(data_column, label=name)

        self.ax.legend()

        self.plot_canvas.draw()
        self.plot_canvas.flush_events()

    def execute(self):
        arguments = self.get_func_inputs()

        value = arguments['']

        if arguments['Добавить'] is not None:
            self.metrics.append(value)

        else:
            self.metrics = []
            print(self.metrics)
            self.start_metrics = []

        self.draw()

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Optimization Plot', 'Plots'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
