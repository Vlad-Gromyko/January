import customtkinter as ctk
import numpy as np
from numpy.ma.core import array

from application.core.services.nodes.node import INode
from application.widgets.maskwidget import MaskLabel

from application.core.utility.mask import Mask


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Заряд', self.palette['NUM'])
        self.add_output_socket('', self.palette['HOLOGRAM'])
        self.load_data = kwargs
        self.widget_width = 200
        self.widget_height = 130
        frame_widgets = ctk.CTkFrame(self.canvas, width=self.widget_width, height=self.widget_height)
        self.frame_IDs['widgets'] = self.canvas.create_window(self.x, self.y, window=frame_widgets,
                                                              anchor=ctk.NW, width=self.widget_width,
                                                              height=self.widget_height)

        self.mask_label = MaskLabel(frame_widgets, Mask(np.zeros((1200, 1920))), size_scale=1 / 10)
        self.mask_label.grid(padx=5, pady=5)

        self.array = None
        if 'holo' in kwargs.keys():
            self.array = kwargs['holo']
            self.mask_label.set_mask(Mask(self.array))
            self.output_sockets[''].set_value(Mask(self.array))

    def execute(self):
        arguments = self.get_func_inputs()

        width = self.event_bus.get_field('slm width')
        height = self.event_bus.get_field('slm height')

        x = np.linspace(-width / 2, width / 2, width)
        y = np.linspace(-height / 2, height / 2, height)

        x, y = np.meshgrid(x, y)

        rho = np.sqrt(x ** 2 + y ** 2)

        phi = np.arctan2(y, x)
        phi = phi + np.min(phi)

        phi = np.flip(phi, 1)

        self.array = phi

        mask = Mask(phi * arguments['Заряд'])

        self.mask_label.set_mask(mask)

        self.output_sockets[''].set_value(mask)

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Вихрь', 'hologram'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
