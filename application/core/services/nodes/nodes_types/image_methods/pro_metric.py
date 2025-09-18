import customtkinter as ctk
import os
from application.core.events import Event
from application.core.services.nodes.node import INode
from tkinter.filedialog import askdirectory
from matplotlib import cm
from PIL import Image
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
import numpy as np
from skimage import restoration

class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Изображение', self.palette['CAMERA_SHOT'])



        self.add_output_socket('Отфильтрованное изображение', self.palette['CAMERA_SHOT'])
        self.add_output_socket('Шум', self.palette['CAMERA_SHOT'])

        self.add_output_socket('MDS', self.palette['NUM'])

        self.load_data = kwargs
        self.strong_control = False

        self.widget_width = 550
        self.widget_height = 700
        frame_widgets = ctk.CTkFrame(self.canvas, width=self.widget_width, height=self.widget_height)
        self.frame_IDs['widgets'] = self.canvas.create_window(self.x, self.y, window=frame_widgets,
                                                              anchor=ctk.NW, width=self.widget_width,
                                                              height=self.widget_height)
        self.check_var = ctk.StringVar(value="on")
        self.checkbox = ctk.CTkCheckBox(frame_widgets, text="Адаптивный центр",
                                        variable=self.check_var, onvalue="on", offvalue="off")
        self.checkbox.grid(row=0, column=0, padx=5, pady=5)

        self.check_var_back = ctk.StringVar(value="on")
        self.checkbox_back = ctk.CTkCheckBox(frame_widgets, text="Вычитание фона",
                                        variable=self.check_var_back, onvalue="on", offvalue="off")
        self.checkbox_back.grid(row=1, column=0, padx=5, pady=5)

        background_methods = ['rolling ball', 'circle', 'corners']

        self.combo_back = ctk.CTkComboBox(frame_widgets, values=background_methods, state='readonly',)
        self.combo_back.set('rolling ball')
        self.combo_back.grid(row=2, column=0, padx=5, pady=5)

        self.back_entry = ctk.CTkEntry(frame_widgets)
        self.back_entry.insert(0, '10')
        self.back_entry.grid(row=2, column=1, padx=5, pady=5)


        self.fig = Figure(figsize=(5, 5), dpi=100)

        self.ax = self.fig.add_subplot(111)

        self.plot_canvas = FigureCanvasTkAgg(self.fig,
                                             master=frame_widgets)
        self.plot_canvas.draw()

        self.plot_canvas.get_tk_widget().grid(columnspan=2)

    def execute(self):
        arguments = self.get_func_inputs()

        image = arguments['Изображение']

        noise = np.zeros_like(image)

        w, h = np.shape(image)

        x = np.linspace(-h / 2, h / 2, h)
        y = np.linspace(-w / 2, w / 2, w)
        x, y = np.meshgrid(x, y)


        if self.checkbox_back.get() == 'on':
            if self.combo_back.get() == 'rolling ball':
                noise = restoration.rolling_ball(image, radius=int(self.back_entry.get()))
            elif self.combo_back.get() == 'circle':
                noise = self.zero_circle_center(image, int(self.back_entry.get()), 0, 0)
            elif self.combo_back.get() == 'corners':
                corner_size = int(self.back_entry.get())
                corners = [
                    image[:corner_size, :corner_size],      # верхний левый
                    image[:corner_size, w-corner_size:w],    # верхний правый
                    image[h-corner_size:h, :corner_size],    # нижний левый
                    image[h-corner_size:h, w-corner_size:w]  # нижний правый
                ]
                corner_means = [np.mean(corner) for corner in corners]
                background_level = np.mean(corner_means)
                noise = np.ones_like(image) * background_level

        image = image - noise

        if self.checkbox.get() == 'on':
            x_c = np.sum(x * image) / np.sum(image)
            y_c = np.sum(y * image) / np.sum(image)
        else:
            x_c, y_c = 0, 0

        mds = np.sum(((x - x_c) ** 2 + (y - y_c) ** 2) * image) / np.sum(image)


        self.output_sockets['Шум'].set_value(noise)
        self.output_sockets['Отфильтрованное изображение'].set_value(image)

        self.output_sockets['MDS'].set_value(mds)


        self.ax.cla()

        self.ax.imshow(image, cmap='hot')

        self.plot_canvas.draw()
        self.plot_canvas.flush_events()


        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def zero_circle_center(arr, radius, center_x, center_y):

        # Создаем копию массива, чтобы не изменять оригинал
        result = arr.copy()

        # Получаем размеры массива
        height, width = arr.shape


        # Создаем сетку координат
        y_coords, x_coords = np.ogrid[:height, :width]

        # Вычисляем расстояния от каждой точки до центра
        distances = np.sqrt((y_coords - center_y)**2 + (x_coords - center_x)**2)

        # Создаем маску для точек внутри радиуса
        mask = distances <= radius

        # Обнуляем элементы внутри радиуса
        result[mask] = 0

        return result

    @staticmethod
    def zero_out_circle_center(arr, radius, center_x, center_y):

        # Создаем копию массива, чтобы не изменять оригинал
        result = arr.copy()

        # Получаем размеры массива
        height, width = arr.shape



        # Создаем сетку координат
        y_coords, x_coords = np.ogrid[:height, :width]

        # Вычисляем расстояния от каждой точки до центра
        distances = np.sqrt((y_coords - center_y)**2 + (x_coords - center_x)**2)

        # Создаем маску для точек внутри радиуса
        mask = distances >= radius

        # Обнуляем элементы внутри радиуса
        result[mask] = 0

        return result

    @staticmethod
    def create_info():
        return Node, 'Метрики-2', 'Metric'



    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
