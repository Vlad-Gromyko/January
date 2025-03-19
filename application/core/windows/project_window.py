import customtkinter as ctk
from application.core.events import Service, Event

import numpy as np


class ProjectWindow(Service, ctk.CTkToplevel):
    def __init__(self):
        Service.__init__(self)
        ctk.CTkToplevel.__init__(self)
        self.name = 'ProjectWindow'
        self.title('Добро пожаловать')

        self.button_new_project = ctk.CTkButton(self, text='Содать Новый Проект', command=self.create_new_project)
        self.button_new_project.grid(padx=50, pady=50)

        self.button_choose_project = ctk.CTkButton(self, text='Выбрать Проект')
        self.button_choose_project.grid(padx=50, pady=50)

    def create_new_project(self):
        path = 'application/New Project'
        self.withdraw()

        self.event_bus.raise_event(Event('Load', value=path))


        self.event_bus.raise_event(Event('Project Loaded'))

        ar = np.zeros((1200, 1920))

        #self.event_bus.raise_event(Event('Add Atlas', value={'text': 'TEST', 'mask': Mask(ar)}))
        # self.event_bus.raise_event(Event('Canvas Add Node', value=Parameter))
        #self.event_bus.raise_event(Event('Canvas Add Node', value=NumNode))
        #self.event_bus.raise_event(Event('Take Shot'))




    def start_service(self, event):
        pass
