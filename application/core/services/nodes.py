import customtkinter as ctk
import tkinter
from tkinter.simpledialog import askstring
from tkinter.messagebox import showwarning

from application.core.events import Service, Event
from tkinterdnd2 import TkinterDnD, DND_ALL

import os
from application.core.services.node import INode, Enter, Out


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

    def add_node(self, node=INode):
        self.active_tab.add_node(node)

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
            self.add_node()
            self.add_node()

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


class Wire:
    def __init__(self, canvas, enter, out, color):
        self.canvas = canvas

        self.enter = enter
        self.out = out

        self.enter.wire = self
        self.out.wire = self

        self.tag1 = enter.oval_ID
        self.tag2 = out.oval_ID

        self.ID = None
        self.color = color

        self.draw()
        print(self.tag1)
        print(self.tag2)

    def draw(self):
        box1 = self.canvas.coords(self.tag1)

        x1 = (box1[2] + box1[0]) // 2
        y1 = (box1[3] + box1[1]) // 2

        box2 = self.canvas.coords(self.tag2)

        x2 = (box2[2] + box2[0]) // 2
        y2 = (box2[3] + box2[1]) // 2

        if self.ID:
            self.canvas.delete(self.ID)
        self.ID = self.canvas.create_line(x1, y1, x2, y2, fill=self.color, width=3)


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

        self.canvas = tkinter.Canvas(self.canvas_place, width=1120, height=650, bg='#363636')
        self.canvas.grid(row=1, column=0, sticky='nsew')

        self.events_reactions['Canvas Selected'] = lambda event: self.it_is_me(event.get_value())
        self.events_reactions['Accept Canvas Rename'] = lambda event: self.rename(event.get_value()['old_name'],
                                                                                  event.get_value()['new_name'], )

        self.canvas.bind('<Motion>', self.move_wire)

        self.nodes = []

        self.enters_ID = []
        self.outs_ID = []

        self.wiring = False
        self.start_tag = None
        self.wire_color = None
        self.end_tag = None
        self.line_to_draw = None

    def start_wire(self, event, tag):
        self.wiring = True

        self.wire_color = self.canvas.itemcget(tag, 'fill')

        self.start_tag = self.canvas.find_closest(event.x, event.y)[0]

    def end_wire(self, event, tag):

        second_tag = self.canvas.find_closest(event.x, event.y)[0]

        second_color = self.canvas.itemcget(second_tag, 'fill')


        if self.wire_color == second_color and self.check_tag(second_tag):
            first_node = self.find(self.start_tag)
            second_node = self.find(second_tag)
            if type(first_node) != type(second_node):
                self.connect_wire(self.start_tag, second_tag)


        self.wiring = False

        self.canvas.delete(self.line_to_draw)

    def find(self, tag):
        target = None
        for node in self.nodes:
            for enter in node.enters.values():
                if enter.oval_ID == tag:
                    target = enter

            for out in node.outs.values():
                if out.oval_ID == tag:
                    target = out

        return target

    def connect_wire(self, first, second):
        first_node = self.find(first)
        second_node = self.find(second)

        enter_node = first_node if isinstance(first, Enter) else second_node
        out_node = second_node if isinstance(second, Out) else first_node

        wire = Wire(self.canvas, enter_node, out_node, self.wire_color)

    def check_tag(self, tag):
        enter = tag in self.enters_ID
        out = tag in self.outs_ID
        return enter or out

    def move_wire(self, event):
        if self.wiring:
            if self.line_to_draw:
                self.canvas.delete(self.line_to_draw)
            box = self.canvas.bbox(self.start_tag)

            x = (box[2] + box[0]) // 2
            y = (box[3] + box[1]) // 2

            self.line_to_draw = self.canvas.create_line(x, y, event.x - 5, event.y - 5, fill=self.wire_color, width=3)

    def add_node(self, node):
        x = 300
        y = 300
        node = node(self.canvas, x, y)

        self.nodes.append(node)

        for item in node.enters_ovals:
            self.canvas.tag_bind(item, '<Button-1>', lambda event, tag=item: self.start_wire(event, tag))
            self.canvas.tag_bind(item, '<ButtonRelease>', lambda event, tag=item: self.end_wire(event, tag))
            self.enters_ID.append(item)

        for item in node.outs_ovals:
            self.canvas.tag_bind(item, '<Button-1>', lambda event, tag=item: self.start_wire(event, tag))
            self.canvas.tag_bind(item, '<ButtonRelease>', lambda event, tag=item: self.end_wire(event, tag))
            self.outs_ID.append(item)

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
        self.event_bus.raise_event(Event('Canvas Ask Rename', value=self.name))

    def rename(self, old_name, new_name):
        if old_name == self.name:
            self.name = new_name
            self.button_name.configure(text=new_name)

    def close_me(self):
        self.event_bus.raise_event(Event('Canvas Close', value=self.name))
