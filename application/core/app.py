import customtkinter as ctk

from application.core.events import EventBus

from application.core.windows.main_window import MainWindow
from application.core.windows.project_window import ProjectWindow
from application.core.windows.splash_window import SplashWindow

from application.core.services.nodes import NodeEditor
from application.core.services.nodes_catalog import NodeCatalog
from application.core.services.status import StatusBar
from application.core.services.menu import TopMenu
from application.core.services.ordered import Atlas, Combiner
from application.core.services.slm import SLM
from application.core.services.camera import Camera
from application.core.services.zernike import Zernike
from application.core.services.traps import Traps


class App:
    def __init__(self):
        self.event_bus = EventBus()

        ### Windows
        self.main_window = MainWindow()
        self.event_bus.add_service(self.main_window)

        self.project_window = ProjectWindow()
        self.event_bus.add_service(self.project_window)

        self.splash_window = SplashWindow()
        self.event_bus.add_service(self.splash_window)

        ### On main

        self.nodes = NodeEditor(self.main_window)
        self.nodes.grid(row=0, column=0, rowspan=2, columnspan=4)
        self.event_bus.add_service(self.nodes)



        self.menu = TopMenu(self.main_window)
        self.event_bus.add_service(self.menu)

        self.main_window.config(menu=self.menu.menu)

        self.down_notebook = ctk.CTkTabview(self.main_window, anchor='w', height=150)
        self.down_notebook.grid(row=2, column=0, columnspan=3, sticky='ew')


        self.down_notebook.add('Ноды')
        self.down_notebook.add('Атлас')
        self.down_notebook.add('Сумматор')

        self.nodes_catalog = NodeCatalog(self.down_notebook.tab('Ноды'))
        self.nodes_catalog.grid()
        self.event_bus.add_service(self.nodes_catalog)


        self.atlas = Atlas(self.down_notebook.tab('Атлас'))
        self.atlas.grid()
        self.event_bus.add_service(self.atlas)

        self.combiner = Combiner(self.down_notebook.tab('Сумматор'))
        self.combiner.grid()
        self.event_bus.add_service(self.combiner)

        self.right_notebook = ctk.CTkTabview(self.main_window, anchor='w', width=365)
        self.right_notebook.grid(row=0, column=4, columnspan=1, rowspan=2, sticky='nsew', pady=5)

        self.right_notebook.add('Камера')
        self.right_notebook.add('Ловушки')
        self.right_notebook.add('Цернике')
        self.right_notebook.add('Моды')

        self.camera = Camera(self.right_notebook.tab('Камера'))
        self.right_notebook.tab('Камера').grid_columnconfigure([0], weight=1)
        self.camera.grid(sticky='ew', row=0, column=0)
        self.event_bus.add_service(self.camera)

        self.traps = Traps(self.right_notebook.tab('Ловушки'))
        self.traps.grid(sticky='ew', row=0, column=0)
        self.event_bus.add_service(self.traps)

        self.zernike = Zernike(self.right_notebook.tab('Цернике'))
        self.right_notebook.tab('Цернике').grid_columnconfigure([0], weight=1)
        self.zernike.grid(sticky='ew', row=0, column=0)
        self.event_bus.add_service(self.zernike)

        self.down_right = ctk.CTkFrame(self.main_window)
        self.down_right.grid(row=2, column=3, columnspan=2, rowspan=1, sticky='nsew', pady=5, padx=5)

        self.slm = SLM(self.down_right)
        self.slm.grid(sticky='nsew')
        self.event_bus.add_service(self.slm)

        self.status = StatusBar(self.main_window)
        self.status.grid(row=3, column=0, columnspan=5, sticky='ew')

        self.event_bus.add_service(self.status)

    def run(self):
        self.main_window.mainloop()
