import customtkinter as ctk
import os
from application.core.events import Event
from application.core.services.nodes.node import INode
from tkinter.filedialog import askdirectory
from matplotlib import cm
from PIL import Image


import matplotlib.pyplot as plt
import numpy as np


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Изображение', self.palette['CAMERA_SHOT'])

        self.add_output_socket('Изображение - Фон', self.palette['CAMERA_SHOT'],)
        self.add_output_socket('Фон', self.palette['NUM'],)


        self.load_data = kwargs
        self.strong_control = False

        self.widget_width = 200
        self.widget_height = 100
        frame_widgets = ctk.CTkFrame(self.canvas, width=self.widget_width, height=self.widget_height)
        self.frame_IDs['widgets'] = self.canvas.create_window(self.x, self.y, window=frame_widgets,
                                                              anchor=ctk.NW, width=self.widget_width,
                                                              height=self.widget_height)

        self.back_entry = ctk.CTkEntry(frame_widgets)
        self.back_entry.insert(0, '20')
        self.back_entry.grid(row=0, column=0, padx=5, pady=5)

    def execute(self):
        arguments = self.get_func_inputs()

        image = arguments['Изображение']


        w, h = np.shape(image)
        size = int(self.back_entry.get())


        mean_1 = np.mean(image[0:size, 0:size])

        mean_2 = np.mean(image[w-size:w, h-size:h])

        mean_3 = np.mean(image[0:size, h-size:h])

        mean_4 = np.mean(image[w-size:w, 0:size])

        mean = np.mean([mean_1, mean_2, mean_3, mean_4])

        noise = np.ones_like(image) * mean



        self.output_sockets['Изображение - Фон'].set_value(image - noise)
        self.output_sockets['Фон'].set_value(mean)


        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Фон Углы', 'Metric'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
