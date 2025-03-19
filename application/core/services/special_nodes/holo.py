import customtkinter as ctk
import numpy as np

from application.core.services.node import INode
from application.widgets.maskwidget import MaskLabel

from application.core.utility.mask import Mask


class HoloNode(INode):
    def __init__(self, config, editor, canvas, palette, x, y, **kwargs):
        super().__init__(config, editor, canvas, palette, x, y, text='Голограмма', theme='hologram', **kwargs)

        self.add_output_socket('', self.palette['HOLOGRAM'])
        self.add_enter_socket('', self.palette['HOLOGRAM'])

        self.widget_width = 200
        self.widget_height = 130
        frame_widgets = ctk.CTkFrame(self.canvas, width=self.widget_width, height=self.widget_height)
        self.frame_IDs['widgets'] = self.canvas.create_window(self.x, self.y, window=frame_widgets,
                                                              anchor=ctk.NW, width=self.widget_width,
                                                              height=self.widget_height)

        self.mask_label = MaskLabel(frame_widgets, None, size_scale=1 / 10)
        self.mask_label.grid(padx=5, pady=5)


    def execute(self):
        arguments = self.get_func_inputs()

        self.mask_label.set_mask(arguments[''])
        self.output_sockets[''].set_value(self.mask_label.get_mask())

