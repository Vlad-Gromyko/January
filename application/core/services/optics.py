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


class Optics(Service, ctk.CTkToplevel):
    def __init__(self, master):
        Service.__init__(self)
        ctk.CTkToplevel.__init__(self, master)
        self.name = 'Optics'
        self.title(self.name)

        self.withdraw()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.events_reactions['Show/Hide Service Optics'] = lambda event: self.deiconify()

        self.visible = False
        self.attributes('-topmost', True)

        ctk.CTkLabel(self, text='Фокус (мм): ').grid(row=0, column=0, padx=5, pady=5)
        self.focus = ctk.CTkEntry(self)
        self.focus.grid(row=0, column=1, padx=5, pady=5)


    def set_project(self, path):
        config = configparser.ConfigParser()
        config.read(path + '/field.ini')

        self.focus.insert(0, config['LENS']['focus_mm'])


        self.fields['optics focus'] = float(config['LENS']['focus_mm']) * 10 ** (-3)


    def on_closing(self):
        self.visible = False
        self.withdraw()






