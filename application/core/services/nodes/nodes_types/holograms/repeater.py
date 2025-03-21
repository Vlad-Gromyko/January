import customtkinter as ctk
import numpy as np

from application.core.services.nodes.node import INode
from application.widgets.maskwidget import MaskLabel

from application.core.utility.mask import Mask


class Node(INode):
    def __init__(self, config, editor, canvas, x, y, text, theme, **kwargs):
        super().__init__(config, editor, canvas, x, y, text=text, theme=theme, **kwargs)

        self.add_enter_socket('', self.palette['HOLOGRAM'])
        self.add_output_socket('', self.palette['HOLOGRAM'])

        self.widget_width = 200
        self.widget_height = 130
        frame_widgets = ctk.CTkFrame(self.canvas, width=self.widget_width, height=self.widget_height)
        self.frame_IDs['widgets'] = self.canvas.create_window(self.x, self.y, window=frame_widgets,
                                                              anchor=ctk.NW, width=self.widget_width,
                                                              height=self.widget_height)

        self.mask_label = MaskLabel(frame_widgets, Mask(np.zeros((1200, 1920))), size_scale=1 / 10)
        self.mask_label.grid(padx=5, pady=5)

    def execute(self):
        arguments = self.get_func_inputs()

        mask = arguments['']

        self.mask_label.set_mask(mask)

        self.output_sockets[''].set_value(mask)

    @staticmethod
    def create_info():
        return Node, 'Повторитель', 'hologram'


