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

        self.add_enter_socket('', self.palette['CAMERA_SHOT'])

        self.load_data = kwargs
        self.widget_width = 1000
        self.widget_height = 500
        frame_widgets = ctk.CTkFrame(self.canvas, width=self.widget_width, height=self.widget_height)
        self.frame_IDs['widgets'] = self.canvas.create_window(self.x, self.y, window=frame_widgets,
                                                              anchor=ctk.NW, width=self.widget_width,
                                                              height=self.widget_height)

        self.fig = plt.figure(figsize=plt.figaspect(0.5))

        self.cbar = None


        self.ax_1 = self.fig.add_subplot(1, 2, 1, )
        self.ax_2 = self.fig.add_subplot(1, 2, 2, projection='3d')

        self.plot_canvas = FigureCanvasTkAgg(self.fig,
                                             master=frame_widgets)
        self.plot_canvas.draw()

        self.plot_canvas.get_tk_widget().pack()

    def execute(self):
        arguments = self.get_func_inputs()

        image = arguments['']

        shape = np.shape(image)
        y = np.linspace(0, shape[0], shape[0])
        x = np.linspace(0, shape[1], shape[1])
        x, y = np.meshgrid(x, y)

        self.ax_1.cla()
        self.ax_2.cla()


        self.ax_1.imshow(image, cmap='hot')

        surf = self.ax_2.plot_surface(x, y, np.flip(image, axis=1), cmap='hot',)

        self.ax_1.set_title(f'Beam Max/Min : {float(np.max(image)), float(np.min(image))}')


        self.plot_canvas.draw()
        self.plot_canvas.flush_events()

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Beam', 'Plots'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
