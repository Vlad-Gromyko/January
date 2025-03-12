import customtkinter as ctk
from application.core.events import Service, Event
from application.widgets.CTkCode import CTkCodeViewer
import numpy as np
from application.core.utility.mask import Mask
import time


class CodeShow(Service, ctk.CTkToplevel):
    def __init__(self, title, code):
        Service.__init__(self)
        ctk.CTkToplevel.__init__(self)
        self.name = 'CodeShow'
        self.title(title)

        self.code_text = CTkCodeViewer(self, code=code, language='python', theme='monokai', width=500, height=500)
        self.code_text.pack()

        self.resizable(False, False)
        self.focus_set()