import customtkinter as ctk

import numpy as np

import screeninfo
import cv2
from PIL import Image

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

        self.button_on_off = ctk.CTkButton(f, text='Включить камеру')
        self.button_on_off.grid(row=0, column=2, padx=5, pady=5)

        self.camera_label = ctk.CTkLabel(self, text='')
        self.camera_label.grid(pady=5)

        self.camera_work = False
        self.camera_overexposed = False

        self.last_shot = None

        self.events_reactions['Take Shot'] = lambda event: self.take_shot()





    def set_project(self, path):
        config = configparser.ConfigParser()
        config.read(path + '/field.ini')
        self.monitor.insert(0, config['CAMERA']['port'])

    def take_shot(self):
        port = int(self.monitor.get())

        cap = cv2.VideoCapture(port, cv2.CAP_DSHOW)
        ret, frame = cap.read()
        frame = frame
        print(np.max(frame))
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            y, x = np.shape(gray)
            self.camera_label.configure(image=ctk.CTkImage(light_image=Image.fromarray(gray), size=(x//2, y//2)))
            self.camera_status.configure(fg_color='#32CD32', text='Включена')
            self.button_on_off.configure(text='Выключить')
            if np.max(frame)>=255:
                self.camera_status.configure(fg_color='#FFA500', text='Пересвечена')

            if np.max(frame)==0:
                self.camera_status.configure(fg_color='#8B0000', text='Нет излучения')





