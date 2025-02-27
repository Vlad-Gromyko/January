import tkinter as tk
import customtkinter as ctk

from application.core.events import Service, Event

import importlib
import importlib.util
import os
from os import listdir
from os.path import isfile, join


class NodeCatalog(Service, ctk.CTkFrame):
    def __init__(self, master):
        Service.__init__(self)
        ctk.CTkFrame.__init__(self, master)
        self.name = 'NodeCatalog'

        self.scroll = ctk.CTkScrollableFrame(self, width=1145, height=150, orientation='horizontal')
        self.scroll.grid(padx=5, pady=5)

        self.events_reactions['Register Node'] = lambda event: self.register_node(event.get_value())

        self.nodes = []
        self.canvases = []

    def set_project(self, path):
        path = 'application/core/services/nodes'
        self.register_nodes_in_folder(path)

    def register_node(self, node):
        canvas = ctk.CTkCanvas(self.scroll, bg='#333333', width=500, height=500)
        canvas.grid(row=0, column=len(self.canvases), padx=5)

        node_to_draw = node(canvas, 300, 200)
        canvas.create_window(200, 100, window=node_to_draw)
        line = canvas.create_line(0, 0, 300, 300)

        self.nodes.append(node)
        self.canvases.append(canvas)

    def register_nodes_in_folder(self, dir_path):
        files = [f for f in listdir(dir_path) if isfile(join(dir_path, f))]
        for item in files:
            self.dynamic_import(os.path.join(dir_path, item))

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
