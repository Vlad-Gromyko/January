import customtkinter as ctk
import numpy as np

from application.core.services.node import INode
from application.widgets.maskwidget import MaskLabel

from application.core.utility.mask import Mask


class Node(INode):
    def __init__(self, config, editor, canvas, palette, x, y, **kwargs):
        super().__init__(config, editor, canvas, palette, x, y, text='Вихрь', theme='hologram', **kwargs)

        self.add_enter_socket('Заряд', self.palette['NUM'])
        self.add_output_socket('', self.palette['HOLOGRAM'])

        self.widget_width = 200
        self.widget_height = 130
        frame_widgets = ctk.CTkFrame(self.canvas, width=self.widget_width, height=self.widget_height)
        self.frame_IDs['widgets'] = self.canvas.create_window(self.x, self.y, window=frame_widgets,
                                                              anchor=ctk.NW, width=self.widget_width,
                                                              height=self.widget_height)

        self.mask_label = MaskLabel(frame_widgets, Mask(np.zeros((1200, 1920))), size_scale=1 / 10)
        print(self.mask_label.label.cget('width'), self.mask_label.cget('height'))
        self.mask_label.grid(padx=5, pady=5)

    def execute(self):
        arguments = self.get_func_inputs()

        width = int(self.config['SLM']['WIDTH'])
        height = int(self.config['SLM']['HEIGHT'])

        x = np.linspace(-width / 2, width / 2, width)
        y = np.linspace(-height / 2, height / 2, height)

        x, y = np.meshgrid(x, y)

        rho = np.sqrt(x ** 2 + y ** 2)

        phi = np.arctan2(y, x)
        phi = phi + np.min(phi)

        phi = np.flip(phi, 1)

        mask = Mask(phi * arguments['Заряд'])

        self.mask_label.set_mask(mask)

        self.output_sockets[''].set_value(mask)

