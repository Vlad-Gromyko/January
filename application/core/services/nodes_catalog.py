import tkinter as tk
import customtkinter as ctk

from application.core.events import Service, Event

import importlib
import importlib.util
import os
from os import listdir
from os.path import isfile, join
from pathlib import Path


class NodeCatalog(Service, ctk.CTkToplevel):
    def __init__(self, master):
        Service.__init__(self)
        ctk.CTkToplevel.__init__(self, master)
        self.name = 'NodeCatalog'

        self.title(self.name)

        self.events_reactions['Register Node'] = lambda event: self.register_node(event.get_value())

        self.nodes = []
        self.canvases = []

        self.withdraw()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.events_reactions['Show/Hide Service Nodes'] = lambda event: self.deiconify()

        self.visible = False

    def show_and_hide(self):
        if self.visible:
            self.withdraw()
        else:
            self.deiconify()
        self.visible = not self.visible

    def on_closing(self):
        self.visible = False
        self.withdraw()

    def set_project(self, path):
        path = 'application/core/services/nodes_types'
        self.register_nodes_in_folder(path)

    def register_node(self, node):
        self.nodes.append(node)

        self.event_bus.raise_event(Event('Canvas Add Node', value=node))

    def register_nodes_in_folder(self, dir_path):
        for dirpath, _, filenames in os.walk(dir_path):
            for f in filenames:
                if f.split('.')[-1] == 'py':
                    self.dynamic_import(os.path.abspath(os.path.join(dirpath, f)))

    def dynamic_import(self, path):
        module = self.import_module_from_path(path)
        node = module.Node

        self.register_node(node)

    def import_module_from_path(self, path: str):
        file_path = path

        spec = importlib.util.spec_from_file_location(f'nodes__{len(self.nodes)}', file_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        return module

    def start_service(self, event: Event):
        pass
