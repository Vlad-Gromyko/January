import customtkinter as ctk
from math import factorial
import numpy as np

import screeninfo
import cv2
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import os
import configparser

from application.core.events import Service, Event
from application.core.utility.mask import Mask
from application.widgets.maskwidget import MaskLabel


class Zernike(Service, ctk.CTkToplevel):
    def __init__(self, master):
        Service.__init__(self)
        ctk.CTkToplevel.__init__(self, master)
        self.name = 'Zernike'
        self.title(self.name)

        self.notebook = ctk.CTkTabview(self)
        self.notebook.grid()
        self.notebook.add('Маски')

        self.notebook.tab('Маски').grid_columnconfigure([0], weight=1)

        ctk.CTkLabel(self.notebook.tab('Маски'), text='Последняя Вычисленная Маска').grid(row=0, column=0, sticky='ew',
                                                                                          pady=5)
        self.auto_total_label = MaskLabel(self.notebook.tab('Маски'), size_scale=1 / 7)
        self.auto_total_label.grid(row=1, column=0, pady=5)

        ctk.CTkLabel(self.notebook.tab('Маски'), text='Введенная маска').grid(row=2, column=0, sticky='ew', pady=5)
        self.hand_total_label = MaskLabel(self.notebook.tab('Маски'), size_scale=1 / 7)
        self.hand_total_label.grid(row=3, column=0, pady=5)

        self.notebook.add('Ввод')

        ctk.CTkButton(self.notebook.tab('Ввод'), text='Рассчет', command=self.calculate_hand).grid(row=0, column=0,
                                                                                                   padx=5, pady=5)
        ctk.CTkButton(self.notebook.tab('Ввод'), text='Очистить', fg_color='#8B0000', command=self.clear).grid(row=0,
                                                                                                               column=1,
                                                                                                               padx=5,
                                                                                                               pady=5)

        self.scroll = ctk.CTkScrollableFrame(self.notebook.tab('Ввод'), width=315, height=480, orientation='vertical')
        self.scroll.grid(row=1, column=0, columnspan=2, pady=5)

        self.slm_width = 0
        self.slm_height = 0

        self.pixel_in_um = 0

        self.r = 0

        self.phi = 0

        self.entries = []

        self.names = [
            ('Константа', 0, 0),
            ('Наклон-Y', -1, 1),
            ('Наклон-X', 1, 1),
            ('Астигматизм-45', -2, 2),
            ('Дефокус', 0, 2),
            ('Астигматизм-90', 2, 2),
            ('Трефойл-45', -3, 3),
            ('Кома-Y', -1, 3),
            ('Кома-X', 1, 3),
            ('Трефойл-90', 3, 3),
        ]

        for counter, item in enumerate(self.names):
            f = self.scroll
            ctk.CTkLabel(f, text=str(counter)).grid(row=counter, column=0, padx=5, pady=5)
            ctk.CTkLabel(f, text=item[0]).grid(row=counter, column=1, padx=5, pady=5)
            ctk.CTkLabel(f, text=f'm = {item[1]}').grid(row=counter, column=2, padx=5, pady=5)
            ctk.CTkLabel(f, text=f'n = {item[2]}').grid(row=counter, column=3, padx=5, pady=5)
            entry = ctk.CTkEntry(f, width=60)
            entry.insert(0, '0')
            entry.grid(row=counter, column=4, padx=5, pady=5)
            self.entries.append(entry)
            ctk.CTkButton(f, text='\u26F6', width=20, command=lambda n=counter: self.show_mask(n)).grid(
                row=counter,
                column=5, padx=5,
                pady=5)

        self.zernike_masks = []
        self.withdraw()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.events_reactions['Show/Hide Service Zernike'] = lambda event: self.deiconify()

        self.visible = False
        self.attributes('-topmost', True)

    def show_and_hide(self):
        if self.visible:
            self.withdraw()
        else:
            self.deiconify()
        self.visible = not self.visible

    def on_closing(self):
        self.visible = False
        self.withdraw()

    def show_mask(self, num):
        im = plt.imshow((self.zernike_masks[num] * float(self.entries[num].get())) % (2 * np.pi))
        plt.colorbar(im)
        plt.show()

    def clear(self):
        for entry in self.entries:
            entry.delete(0, 'end')
            entry.insert(0, '0')

    def set_project(self, path):
        folder = path
        config = configparser.ConfigParser()
        config.read(folder + '/field.ini')


        self.slm_width = int(config['SLM']['WIDTH'])
        self.slm_height = int(config['SLM']['HEIGHT'])

        self.pixel_in_um = int(config['SLM']['PIXEL_IN_UM'])

        self.hand_total_label.set_mask(Mask(np.zeros((self.slm_height, self.slm_width))))
        self.auto_total_label.set_mask(Mask(np.zeros((self.slm_height, self.slm_width))))

        self.hand_total_label.menu.add_command(label='Добавить в Атлас',
                                               command=lambda: self.event_bus.raise_event(
                                                   Event('Add Atlas',
                                                         {'mask': self.hand_total_label.get_mask(),
                                                          'text': 'Цернике'})))

        self.hand_total_label.menu.add_command(label='Добавить в Сумматор',
                                               command=lambda: self.event_bus.raise_event(
                                                   Event('Add Combiner',
                                                         {'mask': self.hand_total_label.get_mask(),
                                                          'text': 'Цернике'})))

        self.hand_total_label.menu.add_command(label='Добавить на Холст',
                                               command=lambda: self.event_bus.raise_event(
                                                   Event('Add Node Holo',
                                                         {'mask': self.hand_total_label.get_mask(),
                                                          'text': 'Цернике'})))

        ####

        self.auto_total_label.menu.add_command(label='Добавить в Атлас',
                                               command=lambda: self.event_bus.raise_event(
                                                   Event('Add Atlas',
                                                         {'mask': self.auto_total_label.get_mask(),
                                                          'text': 'Цернике'})))

        self.auto_total_label.menu.add_command(label='Добавить в Сумматор',
                                               command=lambda: self.event_bus.raise_event(
                                                   Event('Add Combiner',
                                                         {'mask': self.auto_total_label.get_mask(),
                                                          'text': 'Цернике'})))

        self.auto_total_label.menu.add_command(label='Добавить на Холст',
                                               command=lambda: self.event_bus.raise_event(
                                                   Event('Add Node Holo',
                                                         {'mask': self.auto_total_label.get_mask(),
                                                          'text': 'Цернике'})))

        radius_y = 1

        radius_x = radius_y / self.slm_height * self.slm_width

        _x = np.linspace(-radius_x, radius_x, self.slm_width)
        _y = np.linspace(-radius_y, radius_y, self.slm_height)

        _x, _y = np.meshgrid(_x, _y)

        self.r = np.sqrt(_x ** 2 + _y ** 2)

        self.phi = np.arctan2(_y, _x)

        for k in self.names:
            self.zernike_masks.append(self.zernike(k[2], k[1]))

        self.events_reactions['Calculate Zernike One'] = lambda event: self.calculate_one(event.get_value()['number'], event.get_value()['amplitude'])
        self.fields['Last Zernike Mask'] = None

    def calculate_one(self, number, amplitude):
        array = np.zeros((self.slm_height, self.slm_width))
        item = self.zernike_masks[int(number)]

        array = array + item * amplitude

        array = array % (2 * np.pi)

        mask = Mask(array)
        self.auto_total_label.set_mask(mask)
        self.fields['Last Zernike Mask'] = mask

        return array

    def calculate(self, weights):
        array = np.zeros((self.slm_height, self.slm_width))

        for counter, item in enumerate(self.zernike_masks):
            array = array + item * weights[counter]

            array = array % (2 * np.pi)

            mask = Mask(array)
            self.auto_total_label.set_mask(mask)
            self.fields['Last Zernike Mask'] = mask
        return array

    def calculate_hand(self):
        array = self.calculate([float(i.get()) for i in self.entries])

        mask = Mask(array)
        self.hand_total_label.set_mask(mask)

    def zernike(self, n, m):

        array = np.zeros((self.slm_height, self.slm_width))
        for k in range(0, int((n - abs(m)) / 2) + 1):
            array = array + (-1) ** k * binom(n - k, k) * binom(n - 2 * k, (n - abs(m)) / 2 - k) * self.r ** (
                    n - 2 * k)

        if m >= 0:
            array = array * np.cos(m * self.phi)
        elif m < 0:
            array = array * np.sin(m * self.phi)

        floor = np.min(array)

        if floor < 0:
            array = array + floor

        return array % (2 * np.pi)


def binom(a: int, b: int):
    a = int(a)
    b = int(b)
    if a >= b:
        return factorial(a) / factorial(b) / factorial(a - b)
    else:
        return 0
