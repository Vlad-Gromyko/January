import customtkinter as ctk
import numpy as np
from PIL import Image

import tkinter as tk
import tkinter.filedialog as fd
import matplotlib.pyplot as plt

from application.core.utility.mask import Mask


class MaskLabel(ctk.CTkFrame):
    def __init__(self, master, mask: Mask = None, size_scale=1 / 3):
        super().__init__(master)
        self.mask = mask
        self.size_scale = size_scale

        self.label = ctk.CTkLabel(self, text='')
        self.label.grid()

        self.menu = tk.Menu(self, tearoff=0)
        self.label.bind('<Button-3>', self.right_click)

        self.menu.add_command(label='Сохранить', command=self.save_bmp)
        self.menu.add_command(label='Показать', command=self.show)

        if mask is not None:
            self.set_mask(mask)

    def show(self):
        im = plt.imshow(self.mask.get_array())
        plt.colorbar(im)
        plt.show()


    def save_bmp(self, mode='bmp'):
        new_file = fd.asksaveasfile(title="Сохранить голограмму", defaultextension=".bmp",
                                    filetypes=[('Numpy', '*.npy'), ('BitMap', '*.bmp*')], confirmoverwrite=True)

        if new_file:
            mode = new_file.name.split('.')[-1]

            array = self.mask.get_array()

            if mode=='npy':
                np.save(new_file.name, array)

            if mode=='bmp':
                array = np.asarray(array / 2 / np.pi * 255, dtype='uint8')
                image = Image.fromarray(array)
                image.save(new_file.name)


    def right_click(self, event):
        self.menu.post(event.x_root, event.y_root)

    def set_mask(self, mask: Mask):
        self.mask = mask
        size_y, size_x = np.shape(mask.get_array())
        array = np.asarray(mask.get_array() / 2 / np.pi * 255, dtype='uint8')
        image = Image.fromarray(array)
        image = ctk.CTkImage(light_image=image, size=(int(size_x * self.size_scale), int(size_y * self.size_scale)))

        self.label.configure(image=image)

    def get_mask(self):
        return self.mask

    def get_pixels(self):
        array = np.asarray(self.mask.get_array() / 2 / np.pi * 255, dtype='uint8')
        return array
