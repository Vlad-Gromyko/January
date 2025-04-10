import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
import matplotlib.pyplot as plt

from application.core.services.nodes.node import INode


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('', self.palette['CAMERA_SHOT'])

        self.add_output_socket('', self.palette['CAMERA_SHOT'])

        self.widget_width = 300
        self.widget_height = 300
        frame_widgets = ctk.CTkFrame(self.canvas, width=self.widget_width, height=self.widget_height)
        self.frame_IDs['widgets'] = self.canvas.create_window(self.x, self.y, window=frame_widgets,
                                                          anchor=ctk.NW, width=self.widget_width,
                                                          height=self.widget_height)

        self.fig = Figure(figsize=(5, 5), dpi=100)

        self.ax = self.fig.add_subplot(111)

        self.plot_canvas = FigureCanvasTkAgg(self.fig,
                                   master=frame_widgets)
        self.plot_canvas.draw()

        # placing the canvas on the Tkinter window
        self.plot_canvas.get_tk_widget().pack()




    def execute(self):
            arguments = self.get_func_inputs()

            photo = arguments['']

            self.ax.imshow(photo, cmap='hot')

            self.plot_canvas.draw()
            self.plot_canvas.flush_events()

            if 'go' in self.output_sockets.keys():
                self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Повторитель', 'camera'

    def prepare_save_spec(self):
        return __file__, self.x, self.y, {}, self.special_id, self.with_signals