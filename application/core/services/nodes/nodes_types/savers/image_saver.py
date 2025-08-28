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

        self.load_data = kwargs
        self.strong_control = True

        self.widget_width = 200
        self.widget_height = 40
        frame_widgets = ctk.CTkFrame(self.canvas, width=self.widget_width, height=self.widget_height)
        self.frame_IDs['widgets'] = self.canvas.create_window(self.x, self.y, window=frame_widgets,
                                                              anchor=ctk.NW, width=self.widget_width,
                                                              height=self.widget_height)
        self.button = ctk.CTkButton(frame_widgets, text='', width=10, height=10, command=self.button_folder)
        self.button.grid(row=0, column=0)

        self.file_folder = ctk.CTkLabel(frame_widgets, text='')
        self.file_folder.grid(row=0, column=1)

        values = ['viridis', 'plasma', 'inferno', 'magma', 'cividis']

        self.combo = ctk.CTkComboBox(frame_widgets, values=values)
        self.combo.set('inferno')
        self.combo.grid(row=1)

        self.folder_name = None

    def button_folder(self):
        ask = askdirectory()
        if ask:
            self.folder_name = ask
            print(ask)

            self.file_folder.configure(text=ask)

    @staticmethod
    def count_files_in_directory(directory):
        # Получаем список всех элементов в директории
        items = os.listdir(directory)

        # Фильтруем только файлы (исключаем поддиректории)
        files = [item for item in items if os.path.isfile(os.path.join(directory, item))]

        return len(files)

    def execute(self):
        arguments = self.get_func_inputs()
        if self.folder_name is not None:
            count = self.count_files_in_directory(self.folder_name)

            cmap = self.combo.get()

            data = arguments['Изображение']

            normalized_data = (data - np.min(data)) / (np.max(data) - np.min(data))

            colormap = cm.get_cmap(cmap)  # или cm.viridis
            mapped_data = colormap(normalized_data)

            image_data = (mapped_data[:, :, :3] * 255).astype(np.uint8)

            image = Image.fromarray(image_data, 'RGB')
            image.save(f'{self.folder_name}/{count}.png')

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Image', 'savers'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
