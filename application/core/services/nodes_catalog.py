import tkinter as tk
import customtkinter as ctk

from application.core.events import Service, Event


class NodeCatalog(Service, ctk.CTkFrame):
    def __init__(self, master):
        Service.__init__(self)
        ctk.CTkFrame.__init__(self, master)
        self.name = 'NodeCatalog'

        self.scroll = ctk.CTkScrollableFrame(self, width=1145, height=150, orientation='horizontal')
        self.scroll.grid(padx=5, pady=5)



    def start_service(self, event: Event):
        pass