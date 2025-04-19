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

        self.load_data = kwargs
        self.widget_width = 30
        self.widget_height = 30
        frame_widgets = ctk.CTkFrame(self.canvas, width=self.widget_width, height=self.widget_height)
        self.frame_IDs['widgets'] = self.canvas.create_window(self.x, self.y, window=frame_widgets,
                                                              anchor=ctk.NW, width=self.widget_width,
                                                              height=self.widget_height)

        self.label.configure(fg_color='#FFF')
        self.label.configure(text_color='#000')

        self.button = ctk.CTkButton(frame_widgets, text='', command=self.go, text_color='#000', fg_color='#FFF',
                                    width=20, height=20)
        self.button.grid(padx=5, pady=5)


        self.strong_control = True

    def go(self):
        self.output_sockets['go'].set_value(True)
        self.output_sockets['go'].set_value(None)

    def execute(self):
        arguments = self.get_func_inputs()

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)
            self.output_sockets['go'].set_value(None)

    def choose(self):
        self.chosen_one = True
        self.label.configure(fg_color='#4682B4')

    def no_choose(self):
        self.chosen_one = False
        self.label.configure(fg_color='#FFF')


    @staticmethod
    def create_info():
        return Node, 'Play', 'program'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
