import customtkinter as ctk

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


class Camera(Service, ctk.CTkFrame):
    def __init__(self, master):
        Service.__init__(self)
        ctk.CTkFrame.__init__(self, master)
        self.name = 'Camera'

        self.grid_columnconfigure([0], weight=1)

        self.camera_status = ctk.CTkLabel(self, text='Выключена', fg_color='#333333')
        self.camera_status.grid(row=0, column=0, sticky='ew', pady=5)

        f = ctk.CTkFrame(self)
        f.grid(sticky='nsew')

        ctk.CTkLabel(f, text='Порт: ').grid(row=0, column=0, padx=5)

        self.monitor = ctk.CTkEntry(f, width=10)
        self.monitor.grid(row=0, column=1, padx=5, pady=5)

        self.button_shot = ctk.CTkButton(f, text='Снимок', command=self.take_shot, width=20)
        self.button_shot.grid(row=0, column=3, padx=5, pady=5)

        self.button_back = ctk.CTkButton(f, text='Фон', command=self.take_back, width=20)
        self.button_back.grid(row=0, column=2, padx=5, pady=5)

        self.last_shot = None
        self.back = None
        self.clear = None

        self.events_reactions['Take Shot'] = lambda event: self.take_shot()
        self.events_reactions['Take Back'] = lambda event: self.take_back()

        self.shots_notebook = ctk.CTkTabview(self, width=350)
        self.shots_notebook.grid(row=2, column=0)
        self.shots_notebook.add('Фон')
        self.shots_notebook.add('Снимок')
        self.shots_notebook.add('Снимок - Фон')

        self.label_back = ctk.CTkLabel(self.shots_notebook.tab('Фон'), text='')
        self.label_back.grid()

        self.label_shot = ctk.CTkLabel(self.shots_notebook.tab('Снимок'), text='')
        self.label_shot.grid()

        self.label_clear = ctk.CTkLabel(self.shots_notebook.tab('Снимок - Фон'), text='')
        self.label_clear.grid()

        self.fields['Back'] = self.back
        self.fields['Shot'] = self.last_shot
        self.fields['Shot - Back'] = self.clear

    def set_project(self, path):
        config = configparser.ConfigParser()
        config.read(path + '/field.ini')
        self.monitor.insert(0, config['CAMERA']['port'])

    def take_shot(self):
        port = int(self.monitor.get())

        cap = cv2.VideoCapture(port, cv2.CAP_DSHOW)
        ret, frame = cap.read()
        self.camera_status.configure(fg_color='#8B0000', text='Выключена')
        if ret:

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            y, x = np.shape(gray)
            self.last_shot = gray
            self.label_shot.configure(image=ctk.CTkImage(light_image=Image.fromarray(gray), size=(x // 2, y // 2)))
            self.refresh_shots()
            self.camera_status.configure(fg_color='#32CD32', text='Включена')
            if np.max(frame) >= 255:
                self.camera_status.configure(fg_color='#FFA500', text='Пересвечена')

            if np.max(frame) == 0:
                self.camera_status.configure(fg_color='#8B0000', text='Нет излучения')

    def take_back(self):
        port = int(self.monitor.get())

        cap = cv2.VideoCapture(port, cv2.CAP_DSHOW)
        ret, frame = cap.read()
        self.camera_status.configure(fg_color='#8B0000', text='Выключена')
        if ret:

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            y, x = np.shape(gray)
            self.back = gray
            self.label_back.configure(image=ctk.CTkImage(light_image=Image.fromarray(gray), size=(x // 2, y // 2)))
            self.refresh_shots()
            self.camera_status.configure(fg_color='#32CD32', text='Включена')
            if np.max(frame) >= 255:
                self.camera_status.configure(fg_color='#FFA500', text='Пересвечена')

            if np.max(frame) == 0:
                self.camera_status.configure(fg_color='#8B0000', text='Нет излучения')

    def refresh_shots(self):
        shot = self.last_shot is not None
        back = self.back is not None

        if shot and back:
            self.clear = np.asarray(
                np.abs(np.asarray(self.last_shot, dtype='int16') - np.asarray(self.back, dtype='int16')), dtype='uint8')

        elif shot:
            self.clear = self.last_shot

        elif back:
            self.clear = self.back

        y, x = np.shape(self.clear)
        self.label_clear.configure(image=ctk.CTkImage(light_image=Image.fromarray(self.clear), size=(x // 2, y // 2)))
