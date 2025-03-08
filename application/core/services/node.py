import tkinter as tk
from ctypes import windll
from tkinter import simpledialog
from tkinter.font import names

import customtkinter as ctk

from application.core.events import Service, Event
from tkinterdnd2 import TkinterDnD, DND_ALL

from abc import ABC, abstractmethod


class IMove:
    def __init__(self, canvas, x, y):
        self.canvas = canvas

        self.x = x
        self.y = y
        self.ID = None

        self.moving = False

    def move_start(self, event):
        self.moving = True

    def move(self, event):
        if self.moving:
            dx = event.x
            dy = event.y

            self.x += dx
            self.y += dy

    def move_end(self, event):
        self.moving = False


class Enter(IMove):
    def __init__(self, canvas, node, x, y, name, color='#FFF'):
        super().__init__(canvas, x, y, )
        self.name = name
        self.color = color
        self.node = node

        self.outer_oval_ID = self.canvas.create_oval(x, y, x + 15, y + 15, fill='#FFF')
        self.oval_ID = self.canvas.create_oval(x + 3, y + 3, x + 12, y + 12, fill=color)
        self.canvas.itemconfigure(self.outer_oval_ID, state='hidden')

        self.canvas.tag_bind(self.oval_ID, '<Enter>', self.on_enter)
        self.canvas.tag_bind(self.oval_ID, '<Leave>', self.on_leave)

        self.text_ID = self.canvas.create_text(x + 17, y, text=name, fill=color, anchor=ctk.NW)

        bounds = self.canvas.bbox(self.text_ID)
        self.width = bounds[2] - bounds[0] + 15
        self.height = bounds[3] - bounds[1]

        self.wire = None

    def on_enter(self, event):
        self.canvas.itemconfigure(self.outer_oval_ID, state='normal')

    def on_leave(self, event):
        self.canvas.itemconfigure(self.outer_oval_ID, state='hidden')

    def move(self, event):
        super().move(event)
        if self.moving:
            self.canvas.move(self.oval_ID, event.x, event.y)
            self.canvas.move(self.outer_oval_ID, event.x, event.y)
            self.canvas.move(self.text_ID, event.x, event.y)
            if self.wire:
                self.wire.draw()

    def forced_move(self, x, y):
        self.canvas.move(self.oval_ID, x, y)
        self.canvas.move(self.outer_oval_ID, x, y)
        self.canvas.move(self.text_ID, x, y)

    def collect_value(self, value):
        self.node.add_value(self.name, value)


class Out(IMove):
    def __init__(self, canvas, node, x, y, name, color='#FFF'):
        super().__init__(canvas, x, y, )
        self.name = name
        self.color = color
        self.node = node

        self.outer_oval_ID = self.canvas.create_oval(x, y, x + 15, y + 15, fill='#FFF')
        self.oval_ID = self.canvas.create_oval(x + 3, y + 3, x + 12, y + 12, fill=color)
        self.canvas.itemconfigure(self.outer_oval_ID, state='hidden')

        self.canvas.tag_bind(self.oval_ID, '<Enter>', self.on_enter)
        self.canvas.tag_bind(self.oval_ID, '<Leave>', self.on_leave)

        self.text_ID = self.canvas.create_text(x, y, text=name, fill=color, anchor=ctk.NE)

        bounds = self.canvas.bbox(self.text_ID)
        self.width = bounds[2] - bounds[0] + 15
        self.height = bounds[3] - bounds[1]

        self.wire = None

    def on_enter(self, event):
        self.canvas.itemconfigure(self.outer_oval_ID, state='normal')

    def on_leave(self, event):
        self.canvas.itemconfigure(self.outer_oval_ID, state='hidden')

    def move(self, event):
        super().move(event)
        if self.moving:
            self.canvas.move(self.oval_ID, event.x, event.y)
            self.canvas.move(self.outer_oval_ID, event.x, event.y)
            self.canvas.move(self.text_ID, event.x, event.y)
            if self.wire:
                self.wire.draw()

    def forced_move(self, x, y):
        self.x += x
        self.y += y
        self.canvas.move(self.oval_ID, x, y)
        self.canvas.move(self.outer_oval_ID, x, y)
        self.canvas.move(self.text_ID, x, y)


class INode(IMove):
    def __init__(self, canvas, x, y, name='Yoooo MAn', color='#0000AA'):
        super().__init__(canvas, x, y)

        self.frame_ID = self.canvas.create_rectangle(x, y, x + 300, y + 300, fill='#000')

        self.label = ctk.CTkLabel(canvas, text=name, fg_color=color, anchor='w')

        self.label_ID = self.canvas.create_window(x, y, window=self.label, anchor=ctk.NW)

        bounds = self.canvas.bbox(self.label_ID)  # returns a tuple like (x1, y1, x2, y2)
        self.label_width = bounds[2] - bounds[0]
        self.label_height = bounds[3] - bounds[1]

        self.label.bind('<Button-1>', self.move_start)
        self.label.bind('<Motion>', self.move)
        self.label.bind('<ButtonRelease>', self.move_end)

        self.enters = {}
        self.outs = {}

        self.max_width_enter = 0
        self.max_width_out = 0

        self.total_height_enter = 0
        self.total_height_out = 0

        self.enters_ovals = []
        self.outs_ovals = []

        self.wiring = False

        self.add_enter('Input 1', '#00AA00')
        self.add_enter('Input 11111111111111111111', '#0000AA')

        self.add_out('4', '#BB00AA')
        self.add_out('Out 11111111111111111111', '#0045CC')
        self.add_out('Out', '#0000AA')
        self.add_out('O', '#1445CC')
        self.add_out('IYooo', '#00AA00')

        self.redraw_label()

        self.functions_inputs = {}
        for item in self.enters.keys():
            self.functions_inputs[item] = None

        self.functions_outputs = {}
        for item in self.outs.keys():
            self.functions_outputs[item] = None

    def add_value(self, name, value):
        self.functions_inputs[name] = value
        if None not in self.functions_inputs.values():
            self.execute()

    def execute(self):
        self.command()

    def command(self):
        pass

    def add_enter(self, name, color='#FFF'):
        if name not in self.enters.keys():
            y = self.y + self.label_height
            for item in self.enters.values():
                y += item.height + 2

            enter = Enter(self.canvas, self, self.x, y, name, color)

            self.enters[name] = enter

            self.max_width_enter = max(self.max_width_enter, enter.width)

            self.total_height_enter += enter.height + 2

            self.enters_ovals.append(enter.oval_ID)

    def add_out(self, name, color='#FFF'):
        if name not in self.outs.keys():
            y = self.y + self.label_height
            for item in self.outs.values():
                y += item.height + 2

            out = Out(self.canvas, self, self.x, y, name, color)

            self.outs[name] = out

            self.max_width_out = max(self.max_width_out, out.width)
            self.outs_ovals.append(out.oval_ID)

            self.total_height_out += out.height + 2

    def redraw_label(self):
        self.canvas.delete(self.label_ID)

        self.label.configure(width=self.max_width_out + self.max_width_enter + 30)

        self.label_ID = self.canvas.create_window(self.x, self.y, window=self.label, anchor=ctk.NW,
                                                  width=self.max_width_out + self.max_width_enter + 30)

        self.canvas.delete(self.frame_ID)

        self.frame_ID = self.canvas.create_rectangle(self.x, self.y,
                                                     self.x + self.max_width_out + self.max_width_enter + 30,
                                                     self.y + max(self.total_height_out,
                                                                  self.total_height_enter) + self.label_height,
                                                     fill='#000')

        self.canvas.tag_lower(self.frame_ID)

        for item in self.outs.values():
            item.forced_move(self.max_width_out + self.max_width_enter + 15, 0)

    def move_start(self, event):
        super().move_start(event)
        for item in self.enters.values():
            item.move_start(event)

        for item in self.outs.values():
            item.move_start(event)

    def move_end(self, event):
        super().move_end(event)
        for item in self.enters.values():
            item.move_end(event)

        for item in self.outs.values():
            item.move_end(event)

    def move(self, event):
        super().move(event)

        for item in self.enters.values():
            item.move(event)

        for item in self.outs.values():
            item.move(event)

        if self.moving:
            self.canvas.move(self.label_ID, event.x, event.y)
            self.canvas.move(self.frame_ID, event.x, event.y)
