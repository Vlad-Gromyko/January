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
from application.core.services.node import INode


class Parameter(INode):
    def __init__(self, config, editor, canvas, palette, x, y, text, theme, **kwargs):
        super().__init__(config, editor, canvas, palette, x, y, text=text, theme=theme, **kwargs)

        color = self.palette[kwargs['type_color']]
        self.add_enter_socket('', color, -16, -self.height + 7)

        self.add_output_socket('', color, self.width + 13, -self.height + 7)

        self.enter_height = 0
        self.output_height = 0

    def command(self):
        value = self.enter_sockets[''].value_to_hold

        self.event_bus.raise_event(Event('Canvas Parameter Changed', {'name': self.text,
                                                                      'value': value}))

        self.output_sockets[''].kick_value(value)

    @staticmethod
    def create_info():
        return Parameter, 'Параметр', 'hologram'


class NumNode(INode):
    def __init__(self, config, editor, canvas, palette, x, y, text, theme, **kwargs):
        super().__init__(config, editor, canvas, palette, x, y, text=text, theme=theme, **kwargs)

        self.add_output_socket('', self.palette['NUM'])

        value = 1
        sv = tkinter.StringVar()
        self.entry = ctk.CTkEntry(self.canvas, width=50, textvariable=sv)
        self.entry.insert(0, str(value))

        self.frame_IDs['entry'] = self.canvas.create_window(self.x, self.y + self.height, window=self.entry,
                                                            anchor=ctk.NW)

        sv.trace("w", lambda *args: self.execute())
        self.execute()

    def execute(self):
        value = (self.entry.get())
        try:
            value = float(value)
            self.output_sockets[''].set_value(float(value))
        except ValueError:
            pass

    @staticmethod
    def create_info():
        return NumNode, 'Число', 'hologram'

