import customtkinter as ctk
import os
from application.core.events import Event
from application.core.services.nodes.node import INode
from tkinter.filedialog import askdirectory
from matplotlib import cm
from PIL import Image
from skimage.metrics import structural_similarity as ssim

import numpy as np


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Изображение', self.palette['CAMERA_SHOT'])

        self.metrics = ['MDS', 'Сигма', 'DDSIM + 1', 'PIB', 'Shift']

        self.add_output_socket('MDS', self.palette['NUM'], )
        self.add_output_socket('Сигма', self.palette['NUM'], )
        self.add_output_socket('DDSIM + 1', self.palette['NUM'], )
        self.add_output_socket('PIB', self.palette['NUM'], )
        self.add_output_socket('Shift', self.palette['NUM'], )

        self.add_output_socket('Произведение', self.palette['NUM'])

        self.add_output_socket('', self.palette['vector1d'], )

        self.load_data = kwargs
        self.strong_control = False

        self.widget_width = 400
        self.widget_height = 400
        frame_widgets = ctk.CTkFrame(self.canvas, width=self.widget_width, height=self.widget_height)
        self.frame_IDs['widgets'] = self.canvas.create_window(self.x, self.y, window=frame_widgets,
                                                              anchor=ctk.NW, width=self.widget_width,
                                                              height=self.widget_height)
        self.check_var = ctk.StringVar(value="on")
        self.checkbox = ctk.CTkCheckBox(frame_widgets, text="Адаптивный центр",
                                        variable=self.check_var, onvalue="on", offvalue="off")
        self.checkbox.grid(row=0, column=0, padx=5, pady=5)

        self.bucket_radius = ctk.CTkEntry(frame_widgets, width=100)
        self.bucket_radius.grid(row=1, column=0, padx=5, pady=5)
        self.bucket_radius.insert(0, "10")

        self.check_vars = {}

        self.calculated_metrics = {}

        self.labels = {}

        for counter, metric in enumerate(self.metrics):
            self.check_vars[metric] = ctk.StringVar(value="on")
            box = ctk.CTkCheckBox(frame_widgets, text=metric, variable=self.check_vars[metric], onvalue="on",
                                  offvalue="off")
            box.grid(row=2 + counter, column=0, padx=5, pady=5, sticky=ctk.W)

            label = ctk.CTkLabel(frame_widgets, text='0')
            label.grid(row=2 + counter, column=1, padx=5, pady=5, sticky=ctk.W)
            self.labels[metric] = label

    def execute(self):
        arguments = self.get_func_inputs()

        image = arguments['Изображение']

        bucket_radius = int(self.bucket_radius.get())

        w, h = np.shape(image)

        x = np.linspace(-h / 2, h / 2, h)
        y = np.linspace(-w / 2, w / 2, w)
        x, y = np.meshgrid(x, y)

        if self.checkbox.get() == 'on':
            x_c = np.sum(x * image) / np.sum(image)
            y_c = np.sum(y * image) / np.sum(image)
        else:
            x_c, y_c = 0, 0

        signal_intensity = np.sum(image * ((x - x_c) ** 2 + (y - y_c) ** 2))
        summ_intensity = np.sum(image)

        distances = np.sqrt((x - x_c) ** 2 + (y - y_c) ** 2)

        bucket_mask = distances <= bucket_radius

        power_in_bucket = np.sum(image[bucket_mask])

        sigma_x = np.sqrt(np.sum((x - x_c) ** 2 * image) / np.sum(image))
        sigma_y = np.sqrt(np.sum((y - y_c) ** 2 * image) / np.sum(image))

        sigma = np.sqrt(sigma_x ** 2 + sigma_y ** 2)

        mask = np.exp(-((x - x_c) ** 2 / sigma ** 2 + (y - y_c) ** 2 / sigma ** 2))

        gauss = mask * np.ones_like(image)

        mds = signal_intensity / summ_intensity

        one_over_pib = summ_intensity / (power_in_bucket + 0.00000000000001)

        image_a = image / np.max(image)
        image_b = gauss / np.max(gauss)

        dssim = (1 - ssim(image_a, image_b, data_range=image_a.max() - image_a.min())) / 2 + 1

        where_max = np.where(image == np.max(image), image, 0)

        x_max = np.sum(x * where_max) / np.sum(where_max)
        y_max = np.sum(y * where_max) / np.sum(where_max)

        shift = 1 + np.sqrt((x_c - x_max) ** 2 + (y_c - y_max) ** 2)

        self.calculated_metrics['MDS'] = mds
        self.calculated_metrics['Сигма'] = sigma
        self.calculated_metrics['DDSIM + 1'] = dssim
        self.calculated_metrics['PIB'] = one_over_pib
        self.calculated_metrics['Shift'] = shift

        self.output_sockets['MDS'].set_value(mds)
        self.labels['MDS'].configure(text=str(mds))
        self.output_sockets['Сигма'].set_value(sigma)
        self.labels['Сигма'].configure(text=str(sigma))
        self.output_sockets['DDSIM + 1'].set_value(dssim)
        self.labels['DDSIM + 1'].configure(text=str(dssim))
        self.output_sockets['PIB'].set_value(one_over_pib)
        self.labels['PIB'].configure(text=str(one_over_pib))
        self.output_sockets['Shift'].set_value(shift)
        self.labels['Shift'].configure(text=str(shift))

        product = 1
        for metric in self.metrics:
            if self.check_vars[metric].get() == 'on':
                product *= self.calculated_metrics[metric]

        self.output_sockets['Произведение'].set_value(product)

        self.output_sockets[''].set_value([mds, sigma, dssim, one_over_pib])

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Морф-Метрики', 'Metric'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
