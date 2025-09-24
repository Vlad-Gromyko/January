import customtkinter as ctk
import tkinter
from tkinter.simpledialog import askstring
from tkinter.messagebox import showwarning

from application.core.events import Service, Event
import application.core.services.nodes.nodes_types.containers.value as container
from application.core.utility.mask import Mask
from tkinterdnd2 import TkinterDnD, DND_ALL

import numpy as np
import os
import configparser
import pickle
import importlib
from pathlib import Path


class NodeEditor(Service, ctk.CTkFrame, TkinterDnD.DnDWrapper):
    def __init__(self, master):
        Service.__init__(self)
        ctk.CTkFrame.__init__(self, master)
        self.name = 'NodeEditor'

        self.frame_buttons = ctk.CTkFrame(self, height=25)
        self.frame_buttons.grid(row=0, column=0, sticky='ew')

        ctk.CTkButton(self.frame_buttons, text='Цветовая схема', width=25, height=25,
                      command=self.show_color_scheme).grid(row=0, column=1, padx=5)

        ctk.CTkButton(self.frame_buttons, text='Инспектор', width=25, height=25,
                      command=self.show_inspector).grid(row=0, column=2, padx=5)

        self.button_action = ctk.CTkButton(self.frame_buttons, text='\u23F5', width=25, height=25, fg_color='#FFF',
                                           text_color='#000',
                                           command=self.start_execute)
        self.button_action.grid(row=0, column=0, padx=5)

        self.add_button = ctk.CTkButton(self.frame_buttons, text='+ Холст', width=25, height=25,
                                        command=self.plus_add_canvas)
        self.add_button.grid(row=0, column=4, padx=5)

        self.add_array_button = ctk.CTkButton(self.frame_buttons, text='+ Переменная', width=25, height=25,
                                              command=self.plus_add_container)
        self.add_array_button.grid(row=0, column=5, padx=5)

        self.add_array_button = ctk.CTkButton(self.frame_buttons, text='T', width=25, height=25,
                                              command=self.add_text)
        self.add_array_button.grid(row=0, column=3, padx=5)

        self.width = 1165
        self.height = 600

        self.active_tab = None
        self.tabs = {}

        self.fields['Canvas Names'] = []

        self.scroll = ctk.CTkScrollableFrame(self.frame_buttons, orientation='horizontal', height=25, width=1050)
        self.scroll.grid(row=0, column=6, padx=5, sticky='ew')

        self.events_reactions['Canvas Close'] = lambda event: self.close_canvas(event.get_value())
        self.events_reactions['Canvas Selected'] = lambda event: self.choose_canvas(event.get_value())
        self.events_reactions['Canvas Ask Rename'] = lambda event: self.rename_canvas(event.get_value())

        self.events_reactions['Canvas Add Node'] = lambda event: self.add_node(event.get_value())

        self.config = None

    def add_text(self):
        ask = askstring('Текстовый Маркер', 'Введите Текст:')
        if ask:
            pass

    def show_inspector(self):
        self.active_tab.containers.deiconify()

    def plus_add_container(self):
        ask = askstring('Добавить', 'Название Переменной:')
        if ask:
            self.active_tab.containers[ask] = 0
            self.add_node(container.Node, name=ask)

    def start_execute(self):
        self.button_action.configure(fg_color='#000', text_color='#FFF')
        self.button_action.update_idletasks()
        self.active_tab.start_execute()
        self.button_action.configure(fg_color='#FFF', text_color='#000')

    def show_color_scheme(self):
        self.active_tab.show_color_scheme()

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
        tab = CanvasTab(self, name, self.config)

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
            self.active_tab.canvas.grid(row=1, column=0, sticky='nsew', columnspan=2)

    def add_node(self, node, special_id=None, x=300, y=300, control=False, **kwargs):
        self.active_tab.add_node(node, special_id, x, y, control, **kwargs)

    def set_project(self, path):
        self.config = configparser.ConfigParser()
        self.config.read(path + '/field.ini')
        canvases_folder = path + '/canvases/'

        folders = os.listdir(canvases_folder)

        if len(folders) == 0:
            pass
        else:
            items = os.listdir(canvases_folder)

            for folder in items:
                self.load_canvas(path + '/canvases/' + folder)

    def load_canvas(self, dir_path):
        self.add_canvas(dir_path.split('/')[-1])
        wires = None
        containers = None
        for dirpath, _, filenames in os.walk(dir_path):

            for f in filenames:
                if 'containers' in f:
                    f.split('/').pop()

                    containers = dir_path + '/' + '/'.join(f)
                    print(f.split('/').pop())

            for f in filenames:
                if f.split('.')[-1] != 'txt' and ('containers' not in dirpath):
                    with open(dir_path + '/' + f, 'rb') as file:
                        loaded_path, loaded_x, loaded_y, loaded_kwargs, loaded_id, loaded_control = pickle.load(file)

                    file = str(Path(__file__).parent)

                    node = self.dynamic_import(Path(file + '/' + str(loaded_path)))
                    self.add_node(node, loaded_id, loaded_x, loaded_y, loaded_control, **loaded_kwargs)

                elif f.split('.')[-1] == 'txt':
                    wires = dir_path + '/' + f

        if containers:

            self.load_containers(containers)

        if wires:
            self.load_wires(wires)

    def load_containers(self, path):
        for file in os.walk(path):
            self.active_tab.containers[file.split('/')[0]] = pickle.load(file)

    def load_wires(self, path):
        with open(path, "r") as file:
            for line in file:
                self.do_wire_file(line)

    def do_wire_file(self, line):
        line = line.strip()
        enter, output = line.split('/')

        enters = enter.split(' ')
        outputs = output.split(' ')

        first = self.find_socket_by_name(enter)
        second = self.find_socket_by_name(output)

        wire = Wire(self, self.active_tab.name, self.active_tab.canvas, first, second, trigger=False)
        self.event_bus.add_service(wire)

    def find_socket_by_name(self, name):

        result = None
        name = name.replace(' ', '')
        for node in self.active_tab.nodes:
            for socket in node.enter_sockets.values():

                if socket.node_socket_name.replace(' ', '') == name:
                    result = socket

            for socket in node.output_sockets.values():

                if socket.node_socket_name.replace(' ', '') == name:
                    result = socket

        return result

    def dynamic_import(self, path):
        module = self.import_module_from_path(path)
        node = module.Node
        return node

    def import_module_from_path(self, path: str):
        file_path = path

        spec = importlib.util.spec_from_file_location(f'nodes__{0}', file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        return module

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


class Wire(Service):
    def __init__(self, editor, tab_name, canvas, first, second, trigger=True):
        super().__init__()
        self.editor = editor
        self.tab_name = tab_name

        self.canvas = canvas
        self.enter = first if first.enter else second
        self.output = second if first.enter else first

        self.ID = None

        self.enter.new_wire(self)
        self.output.new_wire(self)

        self.draw()

        if self.output.get_value() is not None and trigger:
            self.kick_value(self.output.get_value())

    def save_project(self, path):

        if not os.path.exists(path):
            os.mkdir(path)
        if not os.path.exists(path + '/canvases'):
            os.mkdir(path + '/canvases')
        if not os.path.exists(path + '/canvases' + '/' + self.tab_name):
            os.mkdir(path + '/canvases' + '/' + self.tab_name)

        if not os.path.exists(path + '/canvases' + '/' + self.tab_name + '/containers'):
            os.mkdir(path + '/canvases' + '/' + self.tab_name + '/containers')

        if not os.path.exists(path + '/canvases' + '/' + self.tab_name + '/wires.txt'):
            with open((path + '/canvases' + '/' + self.tab_name + '/wires.txt'), 'w') as fp:
                pass

        with open((path + '/canvases' + '/' + self.tab_name + '/wires.txt'), 'a') as fp:
            line = self.enter.node_socket_name + ' / ' + self.output.node_socket_name
            fp.write(line + '\n')

    def kick_value(self, value):
        self.enter.set_value(value)

    def draw(self):
        x_enter, y_enter = self.enter.center(self.enter.oval_ID)
        x_output, y_output = self.output.center(self.output.oval_ID)

        if self.ID:
            self.canvas.delete(self.ID)

        if x_enter >= x_output:
            x_s = (x_output + x_enter) // 2
            y_s = (y_output + y_enter) // 2

            self.ID = self.canvas.create_line(x_enter, y_enter, x_s, y_enter, x_s, y_s, x_s, y_output, x_output,
                                              y_output,
                                              fill=self.enter.color, width=3,
                                              activewidth=5, smooth=1)
        else:

            x0 = x_output + 100
            x1 = x_enter - 100

            y0 = y_enter - 100
            y1 = max(self.enter.node.y + self.enter.node.max_height(),
                     self.output.node.y + self.output.node.max_height()) + 10

            self.ID = self.canvas.create_line(x_enter, y_enter,
                                              x_enter - 10, y_enter,
                                              x_enter - 10, y1,
                                              x_output + 10, y1,
                                              x_output + 10, y_output,
                                              x_output, y_output,
                                              fill=self.enter.color, width=3,
                                              activewidth=5, smooth=1)
        self.canvas.tag_raise(self.ID)
        self.canvas.tag_bind(self.ID, '<Button-3>', self.shut_wire)

    def shut_wire(self, event=None):
        self.enter.wires.remove(self)
        self.output.wires.remove(self)

        self.enter = None
        self.output = None

        self.canvas.delete(self.ID)
        self.event_bus.services.remove(self)


class CanvasTab(Service, ctk.CTkFrame):
    def __init__(self, master, name, config):
        Service.__init__(self)
        ctk.CTkFrame.__init__(self, master.scroll)
        self.name = name

        self.config = config

        self.palette = config['NODES_TYPES']

        self.canvas_place = master

        self.button_name = ctk.CTkButton(self, text=name, fg_color='#000', command=self.choose_me, height=10)
        self.button_name.grid(row=0, column=0, sticky='ew')
        self.button_name.bind('<Button-3>', self.ask_for_rename)

        self.button_close = ctk.CTkButton(self, text='\u2573', fg_color='#000', width=10, height=10,
                                          command=self.close_me)
        self.button_close.grid(row=0, column=1, sticky='ew')

        self.canvas = tkinter.Canvas(self.canvas_place, width=1900, height=1000, bg='#363636')
        self.canvas.grid(row=1, column=0, sticky='nsew')

        self.events_reactions['Canvas Selected'] = lambda event: self.it_is_me(event.get_value())
        self.events_reactions['Accept Canvas Rename'] = lambda event: self.rename(event.get_value()['old_name'],
                                                                                  event.get_value()['new_name'], )

        self.events_reactions['Canvas Add Hologram'] = lambda event: self.it_is_me(event.get_value())

        self.nodes = []

        self.socket_enter_IDs = []
        self.socket_output_IDs = []

        self.socket_enter_to_node_IDs = {}
        self.socket_output_to_node_IDs = {}

        self.wiring = False

        self.wire_start_x = 0
        self.wire_start_y = 0

        self.wire_color = None

        self.wire_line = None

        self.first_socket = None
        self.second_socket = None

        self.canvas.bind('<Button-1>', self.start_move)
        self.canvas.bind('<Button-3>', self.start_move_right)
        self.canvas.bind('<Motion>', self.do_move)
        self.canvas.bind('<ButtonRelease>', self.end_move)

        self.wires = []

        self.shift_x = 0
        self.shift_y = 0

        self.shifting = False

        self.rect_drawing = False
        self.rect_x = 0
        self.rect_y = 0

        self.rect_list = []

        self.rect_ID = None

        self.color_scheme = False

        self.scheme = []

        self.drop_target_register(DND_ALL)

        self.supreme_leader_node = 0

        self.containers = {}

        self.events_reactions['Value Updated'] = lambda event: self.update_container(event)

    def update_container(self, event):
        tab = event.get_value()['tab']
        name = event.get_value()['name']
        value = event.get_value()['value']

        if self == tab:
            self.containers[name] = value

    def save_project(self, path):
        if not os.path.exists(path):
            os.mkdir(path)
        if not os.path.exists(path + '/canvases'):
            os.mkdir(path + '/canvases')
        if not os.path.exists(path + '/canvases' + '/' + self.name):
            os.mkdir(path + '/canvases' + '/' + self.name)
        if not os.path.exists(path + '/canvases' + '/' + self.name + '/containers'):
            os.mkdir(path + '/canvases' + '/' + self.name + '/containers')

        for counter, node in enumerate(self.nodes):
            spec = node.prepare_save_spec()

            with open(f'{path + '/canvases' + '/' + self.name + '/' + str(counter)}.pkl', 'wb') as f:
                pickle.dump(
                    (self.get_relative_path_from_folder(spec[0], 'nodes_types'), spec[1], spec[2], spec[3], spec[4],
                     spec[5]), f)
        for name in self.containers.keys():
            with open(f'{path + '/canvases' + '/' + self.name + '/containers/' + name}.pkl', 'wb') as f:
                pickle.dump(self.containers[name], f)

    @staticmethod
    def get_relative_path_from_folder(abs_path, target_folder):
        parts = list(Path(abs_path).parts)
        base_index = parts.index(target_folder)

        new_path = Path(*parts[base_index:])

        return new_path

    def start_execute(self):
        for node in self.nodes:
            node.no_choose()
            if node.text == 'Старт':
                node.execute()

    def show_color_scheme(self):
        if self.color_scheme:
            self.hide_scheme()
        else:
            self.draw_scheme()
        self.color_scheme = not self.color_scheme

    def draw_scheme(self):
        width = 20

        height = int(self.canvas.cget('height')) - 20

        for name in self.palette.keys():
            if name != 'SIGNAL':
                item = self.canvas.create_text(width, height, anchor=ctk.NW, text=name, fill='#FFF', font="Arial 14")
                self.scheme.append(item)

                bbox = self.canvas.bbox(item)

                width += bbox[2] - bbox[0] + 10

                rect = self.canvas.create_rectangle(bbox[0], bbox[1], bbox[2] + 15, bbox[3], fill='#000')

                self.scheme.append(rect)
                self.canvas.tag_lower(rect)

                width += 17
                circ = self.canvas.create_oval(bbox[2], bbox[1], bbox[2] + 15, bbox[3], fill=self.palette[name])

                self.scheme.append(circ)

    def hide_scheme(self):
        for item in self.scheme:
            self.canvas.delete(item)

    def start_move(self, event):
        tag = self.canvas.find_closest(event.x, event.y)[0]

        for node in self.nodes:
            node.no_choose()

        if tag in self.socket_enter_IDs or tag in self.socket_output_IDs:
            self.first_socket = tag

            socket = self.find_socket(tag)
            self.wire_color = socket.color
            self.wire_start_x, self.wire_start_y = socket.center(tag)

            self.start_wire(event)
        else:
            self.rect_x = event.x
            self.rect_y = event.y

            self.rect_drawing = True

    def start_move_right(self, event):

        self.shift_x = event.x
        self.shift_y = event.y

        self.shifting = True
        for node in self.nodes:
            node.start_move(event)

    def move_all(self, event):

        delta_x = event.x - self.shift_x
        delta_y = event.y - self.shift_y

        rho = 1
        dx, dy = delta_x / rho, delta_y / rho

        for node in self.nodes:
            node.forced_move(dx, dy)

        self.shift_x = event.x
        self.shift_y = event.y

    def start_wire(self, event):
        self.wiring = True

    def do_move(self, event):
        if self.wiring:
            self.draw_wire(event.x, event.y)
        if self.shifting:
            self.move_all(event)
        if self.rect_drawing:
            if self.rect_ID:
                self.canvas.delete(self.rect_ID)
            self.rect_ID = self.canvas.create_rectangle(self.rect_x, self.rect_y, event.x, event.y, fill='#4682B4')
            self.canvas.tag_lower(self.rect_ID)

            for node in self.nodes:
                node.no_choose()
                if min(event.x, self.rect_x) <= node.x <= max(event.x, self.rect_x):
                    if min(event.y, self.rect_y) <= node.y <= max(event.y, self.rect_y):
                        self.rect_list.append(node)
                        node.choose()

    def draw_wire(self, x, y):
        if self.wire_line:
            self.canvas.delete(self.wire_line)

        self.wire_line = self.canvas.create_line(self.wire_start_x, self.wire_start_y, x, y, fill=self.wire_color,
                                                 width=5)

        self.canvas.tag_lower(self.wire_line)

    def end_move(self, event):
        if self.wiring:
            self.wiring = False
            tag = self.canvas.find_closest(event.x, event.y)[0]
            if tag in self.socket_enter_IDs or tag in self.socket_output_IDs:
                if tag != self.first_socket:
                    self.second_socket = tag
                    self.try_connect()

            self.canvas.delete(self.wire_line)

        if self.shifting:
            self.shifting = False
            for node in self.nodes:
                node.end_move(event)

        if self.rect_drawing:
            self.rect_drawing = False
            self.canvas.delete(self.rect_ID)

    def try_connect(self):
        self.first_socket = self.find_socket(self.first_socket)
        self.second_socket = self.find_socket(self.second_socket)

        if self.first_socket.enter ^ self.second_socket.enter:
            if (self.first_socket.color == self.second_socket.color) or (
                    self.first_socket.color == self.palette['ANY']) or (
                    self.second_socket.color == self.palette['ANY']):
                self.connect_wire()

    def are_sockets_connected(self, first, second):
        pass

    def connect_wire(self):
        wire = Wire(self, self.name, self.canvas, self.first_socket, self.second_socket)
        self.event_bus.add_service(wire)

    def find_socket(self, tag):
        if tag in self.socket_enter_to_node_IDs.keys():
            node = self.socket_enter_to_node_IDs[tag]
            return node.enter_sockets_ovals[tag]

        if tag in self.socket_output_to_node_IDs.keys():
            node = self.socket_output_to_node_IDs[tag]
            return node.output_sockets_ovals[tag]

    def add_node(self, node, special_id=None, x=300, y=300, control=False, **kwargs):

        spec = node.create_info()

        if special_id:
            number = special_id
        else:
            number = self.supreme_leader_node

        node = node(number, self.config, self, self.canvas, x, y, control, spec[1],
                    spec[2], **kwargs)

        node.run()

        if len(self.nodes) > 0:
            self.nodes[-1].no_choose()

        for item in self.nodes:
            item.no_choose()

        node.choose()

        self.event_bus.add_service(node)

        self.nodes.append(node)

        if special_id:
            self.supreme_leader_node = max(self.supreme_leader_node, special_id) + 1
        else:
            self.supreme_leader_node += 1

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
