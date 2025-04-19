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


class Laser(Service, ctk.CTkToplevel):
    def __init__(self, master):
        Service.__init__(self)
        ctk.CTkToplevel.__init__(self, master)
        self.name = 'Laser'
        self.title(self.name)

        self.withdraw()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.visible = False
        self.attributes('-topmost', True)

        ctk.CTkLabel(self, text='Длина Волны (нм): ').grid(row=0, column=0, padx=5, pady=5)
        self.wave = ctk.CTkEntry(self)
        self.wave.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(self, text='Перетяжка (мм): ').grid(row=1, column=0, padx=5, pady=5)
        self.waist = ctk.CTkEntry(self)
        self.waist.grid(row=1, column=1, padx=5, pady=5)


    def set_project(self, path):
        pass


    def on_closing(self):
        self.visible = False
        self.withdraw()






