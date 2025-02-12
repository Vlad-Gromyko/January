import customtkinter as ctk
import numpy as np
from PIL import Image

import tkinter as tk


from application.core.utility.mask import Mask


class MaskLabel(ctk.CTkFrame):
    def __init__(self, master, mask: Mask=None, size_scale=1 / 3):
        super().__init__(master)
        self.mask = mask
        self.size_scale = size_scale

        self.label = ctk.CTkLabel(self, text='')
        self.label.grid()

        self.menu = tk.Menu(self, tearoff=0)
        self.label.bind('<Button-3>', self.right_click)


        if mask is not None:
            self.set_mask(mask)

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