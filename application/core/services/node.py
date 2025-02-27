import tkinter as tk
from tkinter import simpledialog
from tkinter.font import names

import customtkinter as ctk

from application.core.events import Service, Event
from tkinterdnd2 import TkinterDnD, DND_ALL

from abc import ABC, abstractmethod


class INode(Service, ctk.CTkFrame):
    def __init__(self,master, width, height, name='Empty', color='#00CC00'):
        Service.__init__(self)
        ctk.CTkFrame.__init__(self, master=master, width=width, height=height)
        self.name = 'Node'

        self.width = width
        self.height = height

        self.label = ctk.CTkLabel(self, text=name, fg_color=color)
        self.label.grid(row=0, column=0, sticky='nsew')

        self.frame = ctk.CTkFrame(self, fg_color='#F00')
        self.frame.grid(row=1, column=0, sticky='nsew')
