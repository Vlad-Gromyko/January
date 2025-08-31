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
        self.add_enter_socket('Порог', self.palette['NUM'])

        self.add_output_socket('Порог', self.palette['NUM'])
        self.add_output_socket('Симметрия', self.palette['NUM'])
        self.add_output_socket('MDS', self.palette['NUM'])
        self.add_output_socket('Эллиптичность', self.palette['NUM'])
        self.add_output_socket('Сумма', self.palette['NUM'])

        self.load_data = kwargs
        self.strong_control = False

        self.widget_width = 200
        self.widget_height = 40
        frame_widgets = ctk.CTkFrame(self.canvas, width=self.widget_width, height=self.widget_height)
        self.frame_IDs['widgets'] = self.canvas.create_window(self.x, self.y, window=frame_widgets,
                                                              anchor=ctk.NW, width=self.widget_width,
                                                              height=self.widget_height)
        self.check_var = ctk.StringVar(value="on")
        self.checkbox = ctk.CTkCheckBox(frame_widgets, text="Адаптивный центр",
                                        variable=self.check_var, onvalue="on", offvalue="off")
        self.checkbox.grid(row=0, column=0, padx=5, pady=5)

    def execute(self):
        arguments = self.get_func_inputs()

        image = arguments['Изображение']

        w, h = np.shape(image)

        x = np.linspace(-h / 2, h / 2, h)
        y = np.linspace(-w / 2, w / 2, w)
        x, y = np.meshgrid(x, y)

        if self.checkbox.get() == 'on':
            x_c = np.sum(x * image) / np.sum(image)
            y_c = np.sum(y * image) / np.sum(image)
        else:
            x_c, y_c = 0, 0

        edge = arguments['Порог']

        result_up = np.where(image >= edge, image, 0)
        result_down = np.where(image < edge, image, 0)

        result_down = np.sum(result_down)

        result_thresh = result_down

        self.output_sockets['Порог'].set_value(result_thresh)

        rotated_0 = np.flip(image, axis=0)
        rotated_1 = np.flip(image, axis=1)

        result_sym = np.sum(np.abs(image - rotated_0) + np.abs(image - rotated_1))
        result_sym = result_sym / np.sum(image)

        self.output_sockets['Симметрия'].set_value(result_sym)

        signal_intensity = np.sum(image * ((x - x_c) ** 2 + (y - y_c) ** 2))
        summ_intensity = np.sum(image)

        result_mds = signal_intensity / summ_intensity
        self.output_sockets['MDS'].set_value(result_mds)

        sigma_x = np.sum((x - x_c) * (x - x_c) * image)
        sigma_y = np.sum((y - y_c) * (y - y_c) * image)

        result_ellipse = np.abs(sigma_x - sigma_y) / np.sum(image)

        self.output_sockets['Эллиптичность'].set_value(result_ellipse)

        self.output_sockets['Сумма'].set_value(result_thresh + result_sym + result_mds + result_ellipse)


        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Все-Метрика', 'Metric'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
