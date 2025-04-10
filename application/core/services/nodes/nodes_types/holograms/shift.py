import customtkinter as ctk
import numpy as np

from application.core.services.nodes.node import INode
from application.widgets.maskwidget import MaskLabel

from application.core.utility.mask import Mask


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('X (мкм)', self.palette['NUM'])
        self.add_enter_socket('Y (мкм)', self.palette['NUM'])
        self.add_output_socket('', self.palette['HOLOGRAM'])

        self.widget_width = 200
        self.widget_height = 130
        frame_widgets = ctk.CTkFrame(self.canvas, width=self.widget_width, height=self.widget_height)
        self.frame_IDs['widgets'] = self.canvas.create_window(self.x, self.y, window=frame_widgets,
                                                              anchor=ctk.NW, width=self.widget_width,
                                                              height=self.widget_height)

        self.mask_label = MaskLabel(frame_widgets, Mask(np.zeros((1200, 1920))), size_scale=1 / 10)
        self.mask_label.grid(padx=5, pady=5)

        self._x = None
        self._y = None

    def execute(self):
        arguments = self.get_func_inputs()

        x = arguments['X (мкм)'] * 10 **-6
        y = arguments['Y (мкм)'] * 10 **-6


        if self._x is None:
            slm_width = self.event_bus.get_field('slm width')
            slm_height = self.event_bus.get_field('slm height')
            slm_pixel = self.event_bus.get_field('slm pixel')

            focus = self.event_bus.get_field('optics focus')
            wave = self.event_bus.get_field('laser wavelength')

            self._x = np.linspace(-slm_width / 2 * slm_pixel, slm_width / 2 * slm_pixel, slm_width)
            self._y = np.linspace(-slm_height / 2 * slm_pixel, slm_height / 2 * slm_pixel, slm_height)

            self._x = self._x * 2 * np.pi / wave / focus
            self._y = self._y * 2 * np.pi / wave / focus

            self._x, self._y = np.meshgrid(self._x, self._y)


        array = self._x * x + self._y * y
        array = array % (2 * np.pi)

        mask = Mask(array)

        self.mask_label.set_mask(mask)

        self.output_sockets[''].set_value(mask)

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Смещение', 'hologram'

    def prepare_save_spec(self):
        return __file__, self.x, self.y, {}, self.special_id, self.with_signals