import customtkinter as ctk
import tkinter
from tkinter.simpledialog import askstring
from tkinter.messagebox import showwarning

from application.core.events import Service, Event
from tkinterdnd2 import TkinterDnD, DND_ALL

import os

from abc import abstractmethod


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

        self.enter = enter
        self.name = text
        self.node = node
        self.text = text
        self.color = color

        flag_anchor = ctk.NW if enter else ctk.NE

        x_oval = x if enter else x - 15
        x_text = x + 15 if enter else x - 15

        self.oval_ID = self.canvas.create_oval(x_oval, y, x_oval + 15, y + 15, fill=self.color)
        self.text_ID = self.canvas.create_text(x_text, y, anchor=flag_anchor, text='  ' + text + '  ', fill=color,
                                               font='Arial 14'
                                               )

        bounds = self.canvas.bbox(self.text_ID)
        self.width = bounds[2] - bounds[0] + 15
        self.height = bounds[3] - bounds[1] + 2

        self.wire = None

        if self.enter:
            editor.socket_enter_IDs.append(self.oval_ID)

            editor.socket_enter_to_node_IDs[self.oval_ID] = node
        else:
            editor.socket_output_IDs.append(self.oval_ID)

            editor.socket_output_to_node_IDs[self.oval_ID] = node

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

        if self.wire:
            self.wire.draw()

    def new_wire(self, wire):
        if self.wire:
            self.wire.shut_wire(0)
        self.wire = wire

    def kick_value(self, value):
        self.node.kick_value(self.name, value)


class INode(CanvasElement):
    def __init__(self, editor, canvas, x, y, text='Node', color_text='#FFF', color_back='#000'):
        super().__init__(editor, canvas, x, y)

        self.func = None
        self.func_enters = dict()

        self.text = text

        self.color_text = color_text
        self.color_back = color_back

        self.label = ctk.CTkLabel(canvas, text=text, text_color=color_text, fg_color=color_back, anchor=ctk.NW)

        self.frame_IDs = dict()

        self.frame_IDs['label'] = self.canvas.create_window(x, y, anchor=ctk.NW, window=self.label)

        bounds = self.canvas.bbox(self.frame_IDs['label'])

        self.height = bounds[3] - bounds[1] + 2

        self.frame_IDs['back'] = None

        self.frame_IDs['tools'] = None

        self.enter_sockets = {}
        self.output_sockets = {}

        self.enter_sockets_ovals = {}
        self.output_sockets_ovals = {}

        self.label.bind('<Button-1>', self.start_move)
        self.label.bind('<Motion>', self.move)
        self.label.bind('<ButtonRelease>', self.end_move)

        self.enter_height = 0
        self.output_height = 0

        self.enter_width = 0
        self.output_width = 0

        self.SIGNAL = '#FFF'
        self.NUM = '#00A9F3'
        self.STR = '#96e441'
        self.BOOL = '#7D0A0A'

        self.apply_signal()

        self.add_enter_socket('Condition', self.BOOL)
        self.add_enter_socket('Str', self.STR)
        self.add_enter_socket('Num', self.NUM)

        self.move_outputs()

    def apply_signal(self):
        self.add_enter_socket('\u23F5', self.SIGNAL)
        self.add_output_socket('\u23F5', self.SIGNAL)

    def kick_value(self, name, value):
        self.func_enters[name] = value
        self.check_for_execute()

    def check_for_execute(self):
        res = all(self.func_enters.values())

        if res:
            self.execute()

    def execute(self):
        self.command()

    def command(self):
        pass

    def max_height(self):
        return max(self.enter_height, self.output_height) + self.height

    def add_enter_socket(self, name, color):
        if name not in self.enter_sockets.keys():
            enter = Socket(self.editor, self.canvas, self, self.x, self.y + self.enter_height + self.height, name,
                           color, enter=True)
            self.enter_height += enter.height
            self.enter_width = max(self.enter_width, enter.width)
            self.enter_sockets[name] = enter
            self.enter_sockets_ovals[enter.oval_ID] = enter
            self.func_enters[name] = None

    def add_output_socket(self, name, color):
        if name not in self.output_sockets.keys():
            output = Socket(self.editor, self.canvas, self, self.x, self.y + self.output_height + self.height, name,
                            color,
                            enter=False)
            self.output_height += output.height
            self.output_width = max(self.output_width, output.width)
            self.output_sockets[name] = output
            self.output_sockets_ovals[output.oval_ID] = output

    def move_outputs(self):
        for value in self.output_sockets.values():
            value.forced_move(self.enter_width + self.output_width + 30, 0)

        width = max(self.enter_width + self.output_width + 30, 100)

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

    def start_move(self, event):
        self.moving = True

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

    def forced_move(self, x, y,):
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
