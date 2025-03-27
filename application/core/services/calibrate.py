import customtkinter as ctk
import tkinter
import numpy as np

import screeninfo
import cv2

import os
import configparser

from customtkinter import CTkLabel

from application.core.events import Service, Event
from application.core.utility.mask import Mask
from application.widgets.maskwidget import MaskLabel


class Calibrate(Service, ctk.CTkToplevel):
    def __init__(self, master):
        Service.__init__(self)
        ctk.CTkToplevel.__init__(self, master)
        self.name = 'SLM Calibration'
        self.title(self.name)

        self.withdraw()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.events_reactions['Show/Hide Service SLM'] = lambda event: self.deiconify()

        self.visible = False
        self.attributes('-topmost', True)

        self.check = ctk.StringVar(value="off")
        self.check_box = ctk.CTkCheckBox(self, text="Калибровочная маска",
                                         variable=self.check, onvalue="on", offvalue="off")

        self.check_box.grid(row=0, column=0, padx=10, pady=2, sticky='ew', columnspan=2)

        ctk.CTkLabel(self, text='X (мкм): ').grid(row=1, column=0, pady=2, sticky='ew')

        self.x = tkinter.StringVar()
        self.entry_x = ctk.CTkEntry(self, textvariable=self.x, width=30)
        self.entry_x.grid(row=1, column=1, pady=2, sticky='ew')
        self.entry_x.insert(0, '0')

        ctk.CTkLabel(self, text='Y (мкм): ').grid(row=2, column=0, pady=2, sticky='ew')

        self.y = tkinter.StringVar()
        self.entry_y = ctk.CTkEntry(self, textvariable=self.y, width=30)
        self.entry_y.grid(row=2, column=1, pady=2, sticky='ew')
        self.entry_y.insert(0, '0')

        ctk.CTkLabel(self, text='Шаг: ').grid(row=3, column=0, pady=2, sticky='ew')

        self.entry_step = ctk.CTkEntry(self, width=30)
        self.entry_step.grid(row=3, column=1, pady=2, sticky='ew')
        self.entry_step.insert(0, '10')

        t = ctk.CTkFrame(self)
        t.grid(row=4, column=0, padx=10, pady=10, columnspan=2)
        font = ctk.CTkFont(size=20, weight='bold')

        ctk.CTkButton(t, text='↑', font=font, width=20, height=20, command=lambda: self.move_calibrate(0, 1)).grid(
            row=0,
            column=1)
        ctk.CTkButton(t, text='←', font=font, width=20, height=20, command=lambda: self.move_calibrate(-1, 0)).grid(
            row=1,
            column=0)
        ctk.CTkButton(t, text='→', font=font, width=20, height=20, command=lambda: self.move_calibrate(1, 0)).grid(
            row=1,
            column=2)
        ctk.CTkButton(t, text='↓', font=font, width=20, height=20, command=lambda: self.move_calibrate(0, -1)).grid(
            row=2,
            column=1)

        self.events_reactions['Show/Hide Service Calibrate'] = lambda event: self.deiconify()

        self.mask = MaskLabel(self, size_scale=1/5)
        self.mask.grid(row=5, column=0, pady=2, sticky='ew', columnspan=2)

        self._x = None
        self._y = None

    def move_calibrate(self, dx, dy):
        x = float(self.entry_x.get())
        y = float(self.entry_y.get())
        step = float(self.entry_step.get())

        if self._x is None:
            slm_width = self.event_bus.get_field('slm width')
            slm_height = self.event_bus.get_field('slm height')
            slm_pixel = self.event_bus.get_field('slm pixel')

            focus = self.event_bus.get_field('optics focus')
            wave = self.event_bus.get_field('laser wavelength')

            self._x = np.linspace(-slm_width / 2 * slm_pixel, slm_width / 2 * slm_pixel, slm_width)
            self._y = np.linspace(-slm_height / 2 * slm_pixel, slm_height / 2 * slm_pixel, slm_height)

            self._x = self._x * 2 * np.pi / wave / focus
            self._y = self._y * 2 * np.pi / wave / focus

            self._x, self._y = np.meshgrid(self._x, self._y)

        self.entry_x.delete(0, 'end')
        self.entry_y.delete(0, 'end')

        new_x = x + dx * step
        new_y = y + dy * step

        self.entry_x.insert(0, str(new_x))
        self.entry_y.insert(0, str(new_y))

        array = self._x * new_x * 10**-6 + self._y * new_y* 10**-6
        array = array % (2 * np.pi)

        mask = Mask(array)

        self.mask.set_mask(mask)

        if self.check.get() == 'on':
            self.event_bus.raise_event(Event('Set SLM Calibrate', mask))

    def on_closing(self):
        self.visible = False
        self.withdraw()
