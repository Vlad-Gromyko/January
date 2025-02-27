import tkinter as tk
from tkinter import simpledialog
from tkinter.font import names

import customtkinter as ctk


from application.core.events import Service, Event
from tkinterdnd2 import TkinterDnD, DND_ALL


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

        self.add_button = ctk.CTkButton(self.frame_buttons, text='\uFF0B', width=25, height=25, command=self.add)
        self.add_button.grid(row=0, column=2, padx=5)

        self.width = 1165
        self.height = 600

        self.file_buttons = {}
        self.file_canvases = {}

        self.events_reactions['Canvas Change'] = lambda event: self.change_canvas(event.get_value())
        self.events_reactions['Canvas Delete'] = lambda event: self.close_canvas(event.get_value())

        self.active_tab = None
        self.active_canvas = None

        self.fields['Canvas Names'] = []








    def set_project(self, path):
        self.add()


    def change_canvas(self, name):
        self.redraw_tabs()

        self.fields['Canvas Names'] = self.file_buttons.keys()

        self.active_tab = self.file_buttons[name]
        self.active_canvas = self.file_canvases[name]

    def close_canvas(self, name):
        self.file_buttons.pop(name)
        self.redraw_tabs()

    def add(self):
        name = str(len(self.file_buttons.keys()))
        tab = TabButton(self.frame_buttons, name)
        self.file_buttons[name] = tab
        self.event_bus.add_service(tab)

        canvas = NodeCanvas(self, name)
        self.file_canvases[name] = canvas
        self.event_bus.add_service(canvas)

        self.event_bus.raise_event(Event('Canvases Change'))
        self.redraw_tabs()
        canvas.grid(row=1, column=0, sticky='ew')

    def redraw_tabs(self):
        self.forget_all()
        for counter, item in enumerate(self.file_buttons.values()):
            item.grid(column=3 + counter, row=0, padx=5)

    def forget_all(self):
        for item in self.file_buttons.values():
            item.grid_forget()
        for item in self.file_canvases.values():
            item.grid_forget()


class NodeCanvas(Service, ctk.CTkFrame, TkinterDnD.DnDWrapper):
    def __init__(self, master, name):
        Service.__init__(self)
        ctk.CTkFrame.__init__(self, master)
        self.name = name

        self.canvas = tk.Canvas(self, width=1165, height=600, bg='#333333')
        self.canvas.grid(row=1, column=0)

        self.events_reactions['Canvas Change'] = lambda event: self.change_canvas(event.get_value())
        self.events_reactions['Canvas Delete'] = lambda event: self.close_canvas(event.get_value())


    def change_canvas(self, name):
        self.grid_forget()
        if self.name == name:
            self.grid()

    def close_canvas(self, name):
        if name == self.name:
            self.grid_forget()

    def add_node(self, node):

        self.event_bus.add_service(node)
        self.canvas.create_window(10, 20, anchor=tk.NW, window=node, width=node.width, height=node.height)


class TabButton(Service, ctk.CTkFrame, TkinterDnD.DnDWrapper):
    def __init__(self, master, name):
        Service.__init__(self)
        ctk.CTkFrame.__init__(self, master)
        self.name = name

        self.button = ctk.CTkButton(self, text=name, width=100, height=25, command=self.choose)
        self.button.grid(row=0, column=0)

        self.cross = ctk.CTkButton(self, text='\u2573', width=25, height=25, fg_color='#c94f4f', command=self.close)
        self.cross.grid(row=0, column=1)

        self.color = self.button.cget('fg_color')

        self.events_reactions['Canvas Change'] = lambda event: self.change_canvas(event.get_value())

    def change_canvas(self, name):
        if self.name != name:
            self.button.configure(fg_color=self.color)
            print(self.color)

    def choose(self):
        self.button.configure(fg_color='#32CD32')
        self.event_bus.raise_event(Event('Canvas Change', self.name))

    def close(self):
        self.grid_forget()
        self.event_bus.raise_event(Event('Canvas Delete', self.name))
