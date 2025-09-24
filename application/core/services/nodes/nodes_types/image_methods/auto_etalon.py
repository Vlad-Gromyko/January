

import customtkinter as ctk
import os
from application.core.events import Event
from application.core.services.nodes.node import INode
from tkinter.filedialog import askdirectory
from matplotlib import cm
from PIL import Image

import numpy as np


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Изображение', self.palette['CAMERA_SHOT'])

        self.add_output_socket('', self.palette['CAMERA_SHOT'])
        self.add_output_socket('Ширина', self.palette['NUM'])

        self.load_data = kwargs
        self.strong_control = False

        self.widget_width = 200
        self.widget_height = 100
        frame_widgets = ctk.CTkFrame(self.canvas, width=self.widget_width, height=self.widget_height)
        self.frame_IDs['widgets'] = self.canvas.create_window(self.x, self.y, window=frame_widgets,
                                                              anchor=ctk.NW, width=self.widget_width,
                                                              height=self.widget_height)

        etalon_types = ['Гаусс', 'Круг', 'Квадрат']

        self.combo = ctk.CTkComboBox(frame_widgets, values=etalon_types)
        self.combo.set(etalon_types[0])
        self.combo.grid(row=0, column=0, padx=5, pady=5)

        self.check_var = ctk.StringVar(value="on")
        self.checkbox = ctk.CTkCheckBox(frame_widgets, text="Адаптивный центр",
                                        variable=self.check_var, onvalue="on", offvalue="off")
        self.checkbox.grid(row=1, column=0, padx=5, pady=5)

    def execute(self):
        arguments = self.get_func_inputs()

        image = arguments['Изображение']

        w, h = np.shape(image)

        x = np.linspace(-h / 2, h / 2, h)
        y = np.linspace(-w / 2, w / 2, w)
        x, y = np.meshgrid(x, y)

        x_coord = 0
        y_coord = 0

        if self.check_var.get() == "on":
            x_coord = int(np.sum(image * x) / np.sum(image))
            y_coord = int(np.sum(image * y) / np.sum(image))

        sigma_x = np.sqrt(np.sum((x - x_coord)**2 * image) / np.sum(image))
        sigma_y = np.sqrt(np.sum((y - y_coord)**2 * image) / np.sum(image))

        sigma = np.sqrt(sigma_x**2 + sigma_y**2)

        print(sigma_x, sigma_y)

        mask = np.zeros_like(image)

        if self.combo.get() == 'Гаусс':
            mask = np.exp(-((x - x_coord)**2 / sigma**2 + (y - y_coord)**2 / sigma**2))
        elif self.combo.get() == 'Квадрат':

            mask = np.logical_and(np.abs(x - x_coord) <= sigma / 2, np.abs(y - y_coord) <= sigma / 2)

            mask = np.where(mask, 1, 0)

        elif self.combo.get() == 'Круг':

            mask = (x - x_coord)**2 + (y - y_coord)**2 <= sigma**2



        result = mask * np.ones_like(image)
        self.output_sockets[''].set_value(result)

        self.output_sockets['Ширина'].set_value(sigma)

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Авто-Эталон', 'Metric'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
