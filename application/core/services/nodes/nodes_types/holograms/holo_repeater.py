import customtkinter as ctk
import numpy as np
from PIL import Image
from tkinter.filedialog import asksaveasfile, askopenfile

from application.core.services.nodes.node import INode
from application.widgets.maskwidget import MaskLabel

from application.core.utility.mask import Mask


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('', self.palette['HOLOGRAM'])
        self.add_output_socket('', self.palette['HOLOGRAM'])

        self.load_data = kwargs
        self.widget_width = 200
        self.widget_height = 160
        frame_widgets = ctk.CTkFrame(self.canvas, width=self.widget_width, height=self.widget_height)
        self.frame_IDs['widgets'] = self.canvas.create_window(self.x, self.y, window=frame_widgets,
                                                              anchor=ctk.NW, width=self.widget_width,
                                                              height=self.widget_height)

        self.mask_label = MaskLabel(frame_widgets, Mask(np.zeros((1200, 1920))), size_scale=1 / 10)
        self.mask_label.grid(row=1, padx=5, pady=5, columnspan=2)

        self.array = None
        if 'holo' in kwargs.keys():
            self.array = kwargs['holo']
            self.mask_label.set_mask(Mask(self.array))
            self.output_sockets[''].set_value(Mask(self.array))

        ctk.CTkButton(frame_widgets, text='S', command=self.save_holo, width=20, height=20).grid(row=2, column=0,
                                                                                                 padx=5, pady=5)

        ctk.CTkButton(frame_widgets, text='+', command=self.load_holo, width=20, height=20).grid(row=2, column=1,
                                                                                                 padx=5, pady=5)

    def save_holo(self):
        self.mask_label.save_bmp()

    def load_holo(self):
        ask = askopenfile(defaultextension='.bmp', filetypes=[('Bitmap', '*.bmp'), ('Numpy', '*.npy')])
        if ask:
            if ask.name.endswith('.bmp'):
                im = Image.open(ask.name)
                array = np.asarray(im)
                self.array = (array / 255 * 2 * np.pi) % (2 * np.pi)

                self.mask_label.set_mask(Mask(self.array))
            elif ask.name.endswith('.npy'):
                array = np.load(ask.name)
                self.array = array

                self.mask_label.set_mask(Mask(array))

            self.output_sockets[''].set_value(Mask(self.array))

    def execute(self):
        arguments = self.get_func_inputs()

        mask = arguments['']

        self.output_sockets[''].set_value(mask)

        self.mask_label.set_mask(mask)

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Голограмма', 'hologram'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
