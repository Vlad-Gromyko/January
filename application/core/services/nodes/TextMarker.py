import tkinter as tk
from tkinter import simpledialog
from tkinter.font import names

import customtkinter as ctk

from application.core.events import Service, Event
from application.core.services.node import INode
from tkinterdnd2 import TkinterDnD, DND_ALL

from abc import ABC, abstractmethod


class Node(INode):
    def __init__(self,master, width, height):
        super().__init__(master, width, height, name='TEST')
        self.name = 'TextLabel'

