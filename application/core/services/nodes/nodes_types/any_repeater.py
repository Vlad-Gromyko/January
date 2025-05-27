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

        self.add_enter_socket('', self.palette['ANY'])

        self.add_output_socket('', self.palette['ANY'])
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

    def execute(self):
        arguments = self.get_func_inputs()

        value = arguments['']


        self.ax.cla()

        if isinstance(value, float) or isinstance(value, int):
            self.ax.text(0.5, 0.5, str(value), ha='center', va='center', size=40)
            self.ax.axis("off")
            self.plot_canvas.draw()
            self.plot_canvas.flush_events()
        elif isinstance(value, bool):

            if value:
                self.ax.text(0.5, 0.5, 'True', ha='center', va='center', size=40)
                self.ax.axis("off")
                self.plot_canvas.draw()
                self.plot_canvas.flush_events()
            else:
                self.ax.text(0.5, 0.5, 'False', ha='center', va='center', size=40)
                self.ax.axis("off")
                self.plot_canvas.draw()
                self.plot_canvas.flush_events()

        elif isinstance(value, Mask):

            self.ax.imshow(value.get_array(), cmap='gray')
            self.plot_canvas.draw()
            self.plot_canvas.flush_events()

        elif isinstance(value, np.ndarray):

            self.ax.imshow(value, cmap='hot')
            self.plot_canvas.draw()
            self.plot_canvas.flush_events()

        elif isinstance(value, list):

            self.ax.plot(value)
            self.plot_canvas.draw()
            self.plot_canvas.flush_events()

        self.output_sockets[''].set_value(arguments[''])

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Повторитель', 'program'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
