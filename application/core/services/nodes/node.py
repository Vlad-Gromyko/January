import customtkinter as ctk
import tkinter
from tkinter.simpledialog import askstring
from tkinter.messagebox import showwarning

from application.core.windows.code_window import CodeShow

from application.core.events import Service, Event
from tkinterdnd2 import TkinterDnD, DND_ALL

import os

from abc import abstractmethod

import inspect


class CanvasElement:
    def __init__(self, editor, canvas, x, y):
        self.name = 'CanvasElement'

        self.editor = editor
        self.canvas = canvas

        self.x = x
        self.y = y

        self.tag = None

        self.moving = False

    def bbox(self, tag):
        bounds = self.canvas.bbox(tag)
        return bounds

    def center(self, tag):
        bounds = self.canvas.bbox(tag)
        x = (bounds[2] + bounds[0]) // 2
        y = (bounds[3] + bounds[1]) // 2

        return x, y


class Socket(CanvasElement):
    def __init__(self, editor, canvas, node, x, y, text, color, enter=True):
        super().__init__(editor, canvas, x, y)

        self._value_to_hold = None

        self.enter = enter
        self.name = text
        self.node = node
        self.text = text
        self.color = color

        self.node_socket_name = f'{node.special_id} {self.name}'
        self.node_socket_name = self.node_socket_name + ' enter' if enter else self.node_socket_name + ' output'

        flag_anchor = ctk.NW if enter else ctk.NE

        x_oval = x if enter else x - 15
        x_text = x + 15 if enter else x - 15

        self.oval_ID = self.canvas.create_oval(x_oval, y, x_oval + 15, y + 15, fill=self.color)
        self.text_ID = self.canvas.create_text(x_text, y, anchor=flag_anchor, text='  ' + text + '  ', fill='#FFF',
                                               font='Arial 14'
                                               )

        bounds = self.canvas.bbox(self.text_ID)
        self.width = bounds[2] - bounds[0] + 15
        self.height = bounds[3] - bounds[1] + 2

        self.wires = []

        if self.enter:
            editor.socket_enter_IDs.append(self.oval_ID)

            editor.socket_enter_to_node_IDs[self.oval_ID] = node
        else:
            editor.socket_output_IDs.append(self.oval_ID)

            editor.socket_output_to_node_IDs[self.oval_ID] = node

    def set_color(self, color, delete_wires=True):
        self.color = color
        self.canvas.itemconfig(self.oval_ID, fill=color)
        if delete_wires:
            for wire in self.wires:
                wire.shut_wire()

    def get_value(self):

        return self._value_to_hold

    def set_value(self, value):
        self._value_to_hold = value

        if not self.enter:
            for wire in self.wires:
                wire.kick_value(self._value_to_hold)

        if self.enter:
            self.node.try_execute()

    def delete_socket(self):
        self.canvas.delete(self.oval_ID)
        self.canvas.delete(self.text_ID)
        for wire in self.wires:
            wire.shut_wire()

    def coords(self, x, y):
        self.x = x
        self.y = y
        self.canvas.move(self.oval_ID, x, y, )
        self.canvas.move(self.text_ID, x, y, )

    def forced_move(self, x, y):

        self.x += x
        self.y += y
        self.canvas.move(self.oval_ID, x, y, )
        self.canvas.move(self.text_ID, x, y, )

        for wire in self.wires:
            wire.draw()

    def new_wire(self, wire):

        self.wires.append(wire)


class INode(CanvasElement, Service):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text='Node', theme='program', **kwargs):
        CanvasElement.__init__(self, editor, canvas, x, y)
        Service.__init__(self)
        self.special_id = special_id
        self.palette = config['NODES_TYPES']

        self.config = config

        self.theme = theme

        self.text = text

        self.color_back = config['NODES_CATEGORIES'][theme]
        self.widget_width = 0
        self.widget_height = 0

        my_font = ctk.CTkFont(family="<Arial>", size=14, weight='bold')
        self.label = ctk.CTkLabel(canvas, text=text, text_color='#FFF', fg_color='#000', font=my_font,
                                  anchor=ctk.NW)

        self.frame_IDs = dict()

        self.frame_IDs['label'] = self.canvas.create_window(x, y, anchor=ctk.NW, window=self.label)

        bounds = self.canvas.bbox(self.frame_IDs['label'])

        self.height = bounds[3] - bounds[1] + 2
        self.width = bounds[2] - bounds[0] + 2

        self.frame_IDs['back'] = None
        self.frame_IDs['widgets'] = None
        self.frame_IDs['info'] = None

        self.enter_sockets = {}
        self.output_sockets = {}

        self.enter_sockets_ovals = {}
        self.output_sockets_ovals = {}

        self.label.bind('<Button-1>', self.start_move_rect)
        self.label.bind('<Motion>', self.move_rect)
        self.label.bind('<ButtonRelease>', self.end_move_rect)

        self.menu = tkinter.Menu(self.canvas, tearoff=0)
        self.label.bind('<Button-3>', self.right_click)

        self.enter_height = 0
        self.output_height = 0

        self.enter_width = 0
        self.output_width = 0

        self.chosen_one = False
        self.visible = False

        self.with_signals = control
        self.strong_control = False

        self.executable = True

        self.load_data = kwargs

    def remove_signal_sockets(self):
        self.executable = False
        for enter in self.enter_sockets.values():

            if enter.color == self.palette['SIGNAL']:
                enter.set_value(None)
        self.executable = True

    @staticmethod
    @abstractmethod
    def create_info():
        return INode,

    @staticmethod
    def possible_to_create():
        return True

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals

    def saves_dict(self):
        enters = dict()
        for item in self.enter_sockets.values():
            enters[item.name + '_enter'] = item.get_value()

        outputs = dict()
        for item in self.output_sockets.values():
            outputs[item.name + '_output'] = item.get_value()

        return {**enters, **outputs}

    def choose(self):
        self.chosen_one = True
        self.label.configure(fg_color='#A9A9A9')

    def no_choose(self):
        self.chosen_one = False
        self.label.configure(fg_color='#000000')

    def get_func_inputs(self):
        func_inputs = dict()

        for item in self.enter_sockets.keys():
            func_inputs[item] = self.enter_sockets[item].get_value()

        self.remove_signal_sockets()
        return func_inputs

    def try_execute(self):
        if self.executable:
            go = True
            white_go = False
            whites = []

            for item in self.enter_sockets.values():

                if item.get_value() is None and item.color != self.palette['SIGNAL']:
                    go = False

                if item.color == self.palette['SIGNAL']:
                    whites.append(item.get_value())

            # print('WHITES', whites, go)
            if any(whites) or len(whites) == 0:
                white_go = True
                # print('GGG')

            if go and white_go:
                # print('execute')
                self.choose()
                circ = self.canvas.create_oval(self.x - 10, self.y - 10, self.x + 10, self.y + 10, fill="#00FF00")
                self.canvas.update_idletasks()
                self.execute()
                self.canvas.delete(circ)
                self.no_choose()
                for name in self.output_sockets.keys():
                    if self.output_sockets[name].color == self.palette['SIGNAL']:
                        self.output_sockets[name].set_value(None)

    def execute(self):
        pass

    def add_clone(self):
        self.editor.add_node(self.__class__)

    def show_info(self):
        pass

    def show_code(self):
        CodeShow(self.text, inspect.getsource(self.execute))

    def delete_node(self):

        for socket in self.enter_sockets.values():
            socket.delete_socket()

        for socket in self.output_sockets.values():
            socket.delete_socket()

        self.editor.nodes.remove(self)

        for item in self.frame_IDs.values():
            if item:
                self.canvas.delete(item)

    def right_click(self, event):
        self.menu.post(event.x_root, event.y_root)

    def add_menu(self):
        if self.strong_control:
            self.with_signals = False
            self.add_signal()
            self.with_signals = True
        else:
            self.menu.add_command(label='Контроль', command=self.add_signal)

        self.menu.add_command(label='Информация    \u003F', command=self.show_info)
        self.menu.add_command(label='Дублировать    +', command=self.add_clone)
        self.menu.add_command(label='Показать Код', command=self.show_code)
        self.menu.add_separator()
        self.menu.add_command(label='Удалить        \u2573', command=self.delete_node)

    def add_signal(self):
        if not self.with_signals:
            width = max(100, self.enter_width + self.output_width + 30, self.widget_width)
            height_e = self.enter_height + self.height - 3
            height_o = self.output_height + self.height - 3
            self.add_enter_socket('go', self.palette['SIGNAL'], -18, -height_e)
            self.add_output_socket('go', self.palette['SIGNAL'], width + 15, -height_o)
        else:
            self.enter_sockets['go'].delete_socket()
            self.output_sockets['go'].delete_socket()
            self.enter_sockets.pop('go')
            self.output_sockets.pop('go')

        self.with_signals = not self.with_signals

    def run(self):
        self.move_outputs()

        self.add_menu()
        if self.with_signals:
            width = max(100, self.enter_width + self.output_width + 30, self.widget_width)
            height_e = self.enter_height + self.height - 3
            height_o = self.output_height + self.height - 3
            self.add_enter_socket('go', self.palette['SIGNAL'], -18, -height_e)
            self.add_output_socket('go', self.palette['SIGNAL'], width + 15, -height_o)

        self.executable = False
        for item in self.load_data.keys():
            if item.endswith('enter'):
                name = item.split('_')[0]
                self.enter_sockets[name].set_value(self.load_data[item])

        for item in self.load_data.keys():
            if item.endswith('output'):
                name = item.split('_')[0]
                self.output_sockets[name].set_value(self.load_data[item])
        self.executable = True

    def max_height(self):
        return max(self.enter_height, self.output_height) + self.height

    def add_enter_socket(self, name, color, dx=0, dy=0):
        if name not in self.enter_sockets.keys():
            enter = Socket(self.editor, self.canvas, self, self.x + dx, self.y + self.enter_height + self.height + dy,
                           name,
                           color, enter=True)
            self.enter_height += enter.height
            self.enter_width = max(self.enter_width, enter.width)
            self.enter_sockets[name] = enter
            self.enter_sockets_ovals[enter.oval_ID] = enter

    def add_output_socket(self, name, color, dx=0, dy=0):
        if name not in self.output_sockets.keys():
            output = Socket(self.editor, self.canvas, self, self.x + dx, self.y + self.output_height + self.height + dy,
                            name,
                            color,
                            enter=False)
            self.output_height += output.height
            self.output_width = max(self.output_width, output.width)
            self.output_sockets[name] = output
            self.output_sockets_ovals[output.oval_ID] = output

    def move_outputs(self):
        width = max(100, self.enter_width + self.output_width + 30, self.widget_width)

        for value in self.output_sockets.values():
            value.forced_move(width, 0)

        self.canvas.delete(self.frame_IDs['label'])
        self.frame_IDs['label'] = self.canvas.create_window(self.x, self.y, anchor=ctk.NW, window=self.label,
                                                            width=width)

        if self.frame_IDs['back']:
            self.canvas.delete(self.frame_IDs['back'])
        self.frame_IDs['back'] = self.canvas.create_rectangle(self.x, self.y,
                                                              self.x + width,
                                                              self.y + max(self.output_height,
                                                                           self.enter_height) + self.height,
                                                              fill='#000')

        self.canvas.tag_lower(self.frame_IDs['back'])

        self.frame_IDs['theme1'] = self.canvas.create_rectangle(self.x + self.width - 5, self.y,
                                                                self.x + width,
                                                                self.y + self.height,
                                                                fill=self.color_back)
        self.canvas.tag_raise(self.frame_IDs['theme1'])

        if self.frame_IDs['widgets']:
            self.canvas.move(self.frame_IDs['widgets'], 0, 2 + max(self.output_height,
                                                                   self.enter_height) + self.height)
        if self.frame_IDs['info']:
            self.canvas.move(self.frame_IDs['info'], width, 0)

    def start_move(self, event):
        self.moving = True

    def start_move_rect(self, event):
        if not self.chosen_one:
            for node in self.editor.nodes:
                node.no_choose()

        self.choose()
        for node in self.editor.nodes:
            if node.chosen_one:
                node.start_move(event)

    def move_rect(self, event):
        for node in self.editor.nodes:
            if node.chosen_one:
                node.move(event)

    def end_move_rect(self, event):
        for node in self.editor.nodes:
            if node.chosen_one:
                node.end_move(event)
        # self.no_choose()

    def end_move(self, event):
        self.moving = False

    def move(self, event):
        if self.moving:
            self.x += event.x
            self.y += event.y

            for value in self.frame_IDs.values():
                if value:
                    self.canvas.move(value, event.x, event.y)

            for value in self.enter_sockets.values():
                value.forced_move(event.x, event.y)

            for value in self.output_sockets.values():
                value.forced_move(event.x, event.y)

    def forced_move(self, x, y, ):
        if self.moving:
            self.x += x
            self.y += y

            for value in self.frame_IDs.values():
                if value:
                    self.canvas.move(value, x, y)

            for value in self.enter_sockets.values():
                value.forced_move(x, y)

            for value in self.output_sockets.values():
                value.forced_move(x, y)
