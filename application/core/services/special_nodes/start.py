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

class Start(INode):
    def __init__(self, editor, canvas, palette, x, y):
        super().__init__(editor, canvas, palette, x, y, text='START', color_text='#000', color_back='#FFF')

        self.add_output_socket('', self.palette['SIGNAL'], self.width + 13, -self.height + 7)
        self.add_enter_socket('', self.palette['SIGNAL'], self.width + 13, -self.height + 7)

        self.enter_height = 0
        self.output_height = 0

    def add_menu(self):
        self.menu.add_command(label='Информация', command=self.show_info)
