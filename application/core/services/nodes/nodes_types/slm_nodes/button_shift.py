import customtkinter as ctk
import numpy as np

from application.core.services.nodes.node import INode
from application.widgets.maskwidget import MaskLabel

from application.core.utility.mask import Mask


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_output_socket('', self.palette['SIGNAL'])
        self.add_output_socket('Голограмма', self.palette['HOLOGRAM'])

        self.load_data = kwargs
        self.widget_width = 330
        self.widget_height = 160
        frame_widgets = ctk.CTkFrame(self.canvas, width=self.widget_width, height=self.widget_height)
        self.frame_IDs['widgets'] = self.canvas.create_window(self.x, self.y, window=frame_widgets,
                                                              anchor=ctk.NW, width=self.widget_width,
                                                              height=self.widget_height)

        self.mask_label = MaskLabel(frame_widgets, Mask(np.zeros((1200, 1920))), size_scale=1 / 10)
        self.mask_label.grid(row=0, column=0)

        self.buttons = ctk.CTkFrame(frame_widgets, width=300, height=300)
        self.buttons.grid(row=0, column=1)

        ctk.CTkButton(self.buttons, text='UP', width=10, height=10, command=lambda: self.button_event(dx=0, dy=1)).grid(
            row=0, column=1)
        ctk.CTkButton(self.buttons, text='LT', width=10, height=10,
                      command=lambda: self.button_event(dx=-1, dy=0)).grid(row=1, column=0)
        ctk.CTkButton(self.buttons, text='RT', width=10, height=10, command=lambda: self.button_event(dx=1, dy=0)).grid(
            row=1, column=2)
        ctk.CTkButton(self.buttons, text='DN', width=10, height=10,
                      command=lambda: self.button_event(dx=0, dy=-1)).grid(row=2, column=1)

        self.entries = ctk.CTkFrame(frame_widgets)
        self.entries.grid(row=1, column=0, columnspan=2)

        ctk.CTkLabel(self.entries, text='X: мкм').grid(row=0, column=0, padx=5, pady=5)
        self.entry_x = ctk.CTkEntry(self.entries, width=50)
        self.entry_x.grid(row=0, column=1, padx=5, pady=5)
        self.entry_x.insert(0, '0')

        ctk.CTkLabel(self.entries, text='Y: мкм').grid(row=0, column=2, padx=5, pady=5)
        self.entry_y = ctk.CTkEntry(self.entries, width=50)
        self.entry_y.grid(row=0, column=3, padx=5, pady=5)
        self.entry_y.insert(0, '0')

        ctk.CTkLabel(self.entries, text='d: мкм').grid(row=0, column=4, padx=5, pady=5)
        self.entry_d = ctk.CTkEntry(self.entries, width=50)
        self.entry_d.grid(row=0, column=5, padx=5, pady=5)
        self.entry_d.insert(0, '500')

        self.array = None
        self._x = None
        self._y = None

    def button_event(self, dx, dy):
        x = float(self.entry_x.get())
        y = float(self.entry_y.get())
        d = float(self.entry_d.get())

        x = x + d * dx
        y = y + d * dy

        self.entry_x.delete(0, ctk.END)
        self.entry_y.delete(0, ctk.END)

        self.entry_x.insert(0, str(x))
        self.entry_y.insert(0, str(y))

        x = x * 10 ** -6
        y = y * 10 ** -6

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

        self.array = self._x * x + self._y * y
        self.array = self.array % (2 * np.pi)

        mask = Mask(self.array)

        self.mask_label.set_mask(mask)

        self.output_sockets['Голограмма'].set_value(mask)
        self.output_sockets[''].set_value(True)
        self.output_sockets[''].set_value(None)

    def execute(self):
        arguments = self.get_func_inputs()
        mask = Mask(self.array)
        self.output_sockets['Голограмма'].set_value(mask)

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Смещение', 'slm'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
