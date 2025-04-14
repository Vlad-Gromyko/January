import customtkinter as ctk
from tkinter import filedialog
from application.core.events import Service, Event
import configparser
import numpy as np
import os
from application.core.services.nodes.nodes_types.start import Node


class ProjectWindow(Service, ctk.CTkToplevel):
    def __init__(self):
        Service.__init__(self)
        ctk.CTkToplevel.__init__(self)
        self.name = 'ProjectWindow'
        self.title('Добро пожаловать')

        self.button_new_project = ctk.CTkButton(self, text='Содать Новый Проект', command=self.create_new_project)
        self.button_new_project.grid(padx=50, pady=50, row=0, column=0)

        self.button_choose_project = ctk.CTkButton(self, text='Выбрать Проект', command=self.open_project)
        self.button_choose_project.grid(padx=50, pady=50, row=1, column=0)

        self.tabs = ctk.CTkTabview(self)
        self.tabs.grid(padx=50, pady=50, row=0, column=1, rowspan=2)

        self.tabs.add('Линза')
        self.tabs.add('Лазер')
        self.tabs.add('Камера')
        self.tabs.add('SLM')

        ctk.CTkLabel(self.tabs.tab('Линза'), text='Фокус (мм): ').grid(row=0, column=0, padx=10, pady=10)
        self.lens_focus = ctk.CTkEntry(self.tabs.tab('Линза'), width=100)
        self.lens_focus.insert(0, '400')
        self.lens_focus.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(self.tabs.tab('Лазер'), text='Длина Волны (нм): ').grid(row=0, column=0, padx=10, pady=10)
        self.wave = ctk.CTkEntry(self.tabs.tab('Лазер'), width=100)
        self.wave.insert(0, '850')
        self.wave.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(self.tabs.tab('Лазер'), text='Перетяжка (мм): ').grid(row=1, column=0, padx=10, pady=10)
        self.waist = ctk.CTkEntry(self.tabs.tab('Лазер'), width=100)
        self.waist.insert(0, '2')
        self.waist.grid(row=1, column=1, padx=10, pady=10)

        ctk.CTkLabel(self.tabs.tab('Камера'), text='Порт: ').grid(row=0, column=0, padx=10, pady=10)
        self.camera_port = ctk.CTkEntry(self.tabs.tab('Камера'), width=100)
        self.camera_port.insert(0, '0')
        self.camera_port.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(self.tabs.tab('Камера'), text='Пиксель (мкм): ').grid(row=1, column=0, padx=10, pady=10)
        self.modeling_pixel_UM = ctk.CTkEntry(self.tabs.tab('Камера'), width=100)
        self.modeling_pixel_UM.insert(0, '3')
        self.modeling_pixel_UM.grid(row=1, column=1, padx=10, pady=10)

        ctk.CTkLabel(self.tabs.tab('Камера'), text='Разрешение: ').grid(row=2, column=0, padx=10, pady=10)
        self.modeling_width = ctk.CTkEntry(self.tabs.tab('Камера'), width=100)
        self.modeling_width.insert(0, '2000')
        self.modeling_width.grid(row=2, column=1, padx=10, pady=10)

        ctk.CTkLabel(self.tabs.tab('SLM'), text='X: ').grid(row=0, column=0, padx=10, pady=10)
        self.width = ctk.CTkEntry(self.tabs.tab('SLM'), width=100)
        self.width.insert(0, '1920')
        self.width.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(self.tabs.tab('SLM'), text='Y: ').grid(row=1, column=0, padx=10, pady=10)
        self.height = ctk.CTkEntry(self.tabs.tab('SLM'), width=100)
        self.height.insert(0, '1200')
        self.height.grid(row=1, column=1, padx=10, pady=10)

        ctk.CTkLabel(self.tabs.tab('SLM'), text='2\u03C0: ').grid(row=2, column=0, padx=10, pady=10)
        self.gray = ctk.CTkEntry(self.tabs.tab('SLM'), width=100)
        self.gray.insert(0, '255')
        self.gray.grid(row=2, column=1, padx=10, pady=10)

        ctk.CTkLabel(self.tabs.tab('SLM'), text='Монитор: ').grid(row=3, column=0, padx=10, pady=10)
        self.monitor = ctk.CTkEntry(self.tabs.tab('SLM'), width=100)
        self.monitor.insert(0, '1')
        self.monitor.grid(row=3, column=1, padx=10, pady=10)

        ctk.CTkLabel(self.tabs.tab('SLM'), text='Пиксель (мкм): ').grid(row=4, column=0, padx=10, pady=10)
        self.slm_pixel = ctk.CTkEntry(self.tabs.tab('SLM'), width=100)
        self.slm_pixel.insert(0, '8')
        self.slm_pixel.grid(row=4, column=1, padx=10, pady=10)

        self.project_path = None

    def write_config(self):
        config = configparser.ConfigParser()

        config['LENS'] = {
            'Focus_MM': self.lens_focus.get(),
        }

        config['LASER'] = {
            'wavelength_NM': self.wave.get(),
            'waist_MM': self.waist.get(),
        }

        config['CAMERA'] = {
            'port': self.camera_port.get(),
            'modeling_pixel_UM': self.modeling_pixel_UM.get(),
            'modeling_width': self.modeling_width.get()
        }

        config['SLM'] = {
            'WIDTH': self.width.get(),
            'HEIGHT': self.height.get(),
            'GRAY': self.gray.get(),
            'MONITOR': self.monitor.get(),
            'PIXEL_IN_UM': self.slm_pixel.get(),
        }

        config['NODES_CATEGORIES'] = {
            'program': '#FFFFFF',
            'zernike': '#00FF00',
            'camera': '#FF8C00',
            'slm': '#4B0082',
            'traps': '#8B0000',
            'hologram': '#00FF00',
            'math': '#191970',
            'container': '#191970',
            'time': '#000000',
        }

        config['NODES_TYPES'] = {
            'signal': '#ECF0F1',
            'bool': '#E74C3C',
            'num': '#3498DB',
            'str': '#379800',
            'hologram': '#2ECC71',
            'camera_shot': '#F39C12',
            'vector1d': '#40E0D0',
            'vector2d': '#AFEEEE',
            'any': '#8E44AD',
        }

        # Записываем конфигурацию в файл
        with open('application/New Project/field.ini', 'w') as configfile:
            config.write(configfile)

    def create_new_project(self):
        self.write_config()
        path = 'application/New Project'
        self.project_path = path
        self.withdraw()

        self.event_bus.raise_event(Event('Load', value=path))

        self.event_bus.raise_event(Event('Canvas Add Node', Node))
        self.event_bus.raise_event(Event('Project Loaded'))

        ar = np.zeros((1200, 1920))

        # self.event_bus.raise_event(Event('Add Atlas', value={'text': 'TEST', 'mask': Mask(ar)}))
        # self.event_bus.raise_event(Event('Canvas Add Node', value=Parameter))
        # self.event_bus.raise_event(Event('Canvas Add Node', value=NumNode))
        # self.event_bus.raise_event(Event('Take Shot'))

    def open_project(self):
        ask = filedialog.askdirectory()
        if ask:
            self.project_path = ask
            self.write_config()
            self.withdraw()

            self.event_bus.raise_event(Event('Load', value=ask))

            self.event_bus.raise_event(Event('Project Loaded'))

    def save_project(self, path):
        config = configparser.ConfigParser()

        config.read(self.project_path + '/field.ini')

        if not os.path.exists(path):
            os.mkdir(path)

        with open(path + '/field.ini', 'w') as configfile:
            config.write(configfile)

    def start_service(self, event):
        pass
