import customtkinter as ctk
from tkinter.simpledialog import askstring
from tkinter.messagebox import showwarning

from application.core.events import Service, Event
from tkinterdnd2 import TkinterDnD, DND_ALL

import os


class NodeEditor(Service, ctk.CTkFrame, TkinterDnD.DnDWrapper):
    def __init__(self, master):
        Service.__init__(self)
        ctk.CTkFrame.__init__(self, master)
        self.name = 'NodeEditor'

        self.frame_buttons = ctk.CTkFrame(self, height=25)
        self.frame_buttons.grid(row=0, column=0, sticky='ew')

        ctk.CTkButton(self.frame_buttons, text='Цветовая схема', width=25, height=25).grid(row=0, column=1, padx=5)

        self.button_action = ctk.CTkButton(self.frame_buttons, text='\u23F5', width=25, height=25)
        self.button_action.grid(row=0, column=0, padx=5)

        self.add_button = ctk.CTkButton(self.frame_buttons, text='\uFF0B', width=25, height=25,
                                        command=self.plus_add_canvas)
        self.add_button.grid(row=0, column=2, padx=5)

        self.width = 1165
        self.height = 600

        self.active_tab = None
        self.tabs = {}

        self.fields['Canvas Names'] = []

        self.scroll = ctk.CTkScrollableFrame(self.frame_buttons, orientation='horizontal', height=25, width=900)
        self.scroll.grid(row=0, column=3, padx=5, sticky='w')

        self.events_reactions['Canvas Close'] = lambda event: self.close_canvas(event.get_value())
        self.events_reactions['Canvas Selected'] = lambda event: self.choose_canvas(event.get_value())
        self.events_reactions['Canvas Ask Rename'] = lambda event: self.rename_canvas(event.get_value())

    def rename_canvas(self, name):
        ask = askstring('Переименовать Холст', 'Название Холста:')
        if ask:
            if ask not in self.tabs.keys():
                self.tabs[ask] = self.tabs[name]
                del self.tabs[name]
                self.event_bus.raise_event(Event('Accept Canvas Rename', {'old_name': name, 'new_name': ask}))
            else:
                showwarning(message="Название " + ask + ' занято')

    def choose_canvas(self, name):
        self.grid_forget_tabs()
        self.active_tab = self.tabs[name]
        self.grid_tabs()

    def plus_add_canvas(self):
        ask = askstring('Добавить Новый Холст', 'Название Холста:')

        if ask:
            if self.validate_name(ask):
                self.add_canvas(ask)
            else:
                showwarning(message="Холст с названием " + ask + ' уже существует')

    def add_canvas(self, name):
        tab = CanvasTab(self, name)

        self.event_bus.add_service(tab)

        self.tabs[name] = tab

        self.event_bus.raise_event(Event('New Canvas', name))
        self.event_bus.raise_event(Event('Canvas Selected', name))

        self.active_tab = tab

        self.grid_tabs()

    def grid_forget_tabs(self):
        for item in self.tabs.values():
            item.canvas.grid_forget()
            item.grid_forget()

    def grid_tabs(self):
        for counter, item in enumerate(self.tabs.values()):
            item.grid(row=0, column=counter)

        if self.active_tab:
            self.active_tab.canvas.grid(row=1, column=0, sticky='nsew')

    def set_project(self, path):
        canvases_folder = path + '/canvases'

        folders = os.listdir(canvases_folder)

        if len(folders) == 0:
            self.add_canvas('Новый Холст')

    def validate_name(self, name: str):
        return not (name in self.tabs.keys())

    def close_canvas(self, name):
        self.grid_forget_tabs()
        self.tabs.pop(name)

        if len(self.tabs) > 0:
            tab = list(self.tabs.keys())[-1]
            self.active_tab = self.tabs[tab]
            self.event_bus.raise_event(Event('Canvas Selected', tab))
        else:
            self.active_tab = None

        self.grid_tabs()


class CanvasTab(Service, ctk.CTkFrame):
    def __init__(self, master, name):
        Service.__init__(self)
        ctk.CTkFrame.__init__(self, master.scroll)
        self.name = name

        self.canvas_place = master

        self.button_name = ctk.CTkButton(self, text=name, fg_color='#000', command=self.choose_me, height=10)
        self.button_name.grid(row=0, column=0, sticky='ew')
        self.button_name.bind('<Button-3>', self.ask_for_rename)

        self.button_close = ctk.CTkButton(self, text='\u2573', fg_color='#000', width=10, height=10,
                                          command=self.close_me)
        self.button_close.grid(row=0, column=1, sticky='ew')

        self.canvas = ctk.CTkCanvas(self.canvas_place, width=1120, height=650, bg='#000')
        self.canvas.grid(row=1, column=0, sticky='nsew')

        self.canvas.create_text(50, 50, text=self.name, fill="#004D40")

        self.events_reactions['Canvas Selected'] = lambda event: self.it_is_me(event.get_value())
        self.events_reactions['Accept Canvas Rename'] = lambda event: self.rename(event.get_value()['old_name'],
                                                                                  event.get_value()['new_name'], )

    def it_is_me(self, name):
        self.button_name.configure(fg_color='#FFF')
        self.button_name.configure(text_color='#000')
        self.button_close.configure(fg_color='#FFF')
        self.button_close.configure(text_color='#000')
        if name != self.name:
            self.button_name.configure(fg_color='#000')
            self.button_name.configure(text_color='#FFF')
            self.button_close.configure(fg_color='#000')
            self.button_close.configure(text_color='#FFF')

    def choose_me(self):
        self.button_name.configure(fg_color='#FFF')
        self.button_name.configure(text_color='#000')
        self.button_close.configure(fg_color='#FFF')
        self.button_close.configure(text_color='#000')

        self.event_bus.raise_event(Event('Canvas Selected', value=self.name))

    def ask_for_rename(self, event):
        print('aaaa')
        self.event_bus.raise_event(Event('Canvas Ask Rename', value=self.name))

    def rename(self, old_name, new_name):
        if old_name == self.name:
            self.name = new_name
            self.button_name.configure(text=new_name)

    def close_me(self):
        self.event_bus.raise_event(Event('Canvas Close', value=self.name))
