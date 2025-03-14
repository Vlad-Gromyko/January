import tkinter as tk
import customtkinter as ctk

from application.core.events import Service, Event

import importlib
import importlib.util
import os
from os import listdir
from os.path import isfile, join
from pathlib import Path


class NodeCatalog(Service, ctk.CTkFrame):
    def __init__(self, master):
        Service.__init__(self)
        ctk.CTkFrame.__init__(self, master)
        self.name = 'NodeCatalog'

        self.events_reactions['Register Node'] = lambda event: self.register_node(event.get_value())

        self.nodes = []
        self.canvases = []

    def set_project(self, path):
        path = 'application/core/services/nodes_types'
        self.register_nodes_in_folder(path)

    def register_node(self, node):
        self.nodes.append(node)

        self.event_bus.raise_event(Event('Canvas Add Node', value=node))



    def register_nodes_in_folder(self, dir_path):
        for dirpath, _, filenames in os.walk(dir_path):
            for f in filenames:
                    if f.split('.')[-1]=='py':
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
