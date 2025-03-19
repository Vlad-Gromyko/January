from application.core.events import EventBus

from application.core.windows.main_window import MainWindow
from application.core.windows.project_window import ProjectWindow
from application.core.windows.splash_window import SplashWindow

from application.core.services.nodes.nodes import NodeEditor
from application.core.services.nodes.nodes_catalog import NodeCatalog
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
        self.nodes.grid(row=0, column=0, sticky='nsew')
        self.event_bus.add_service(self.nodes)

        self.menu = TopMenu(self.main_window)
        self.event_bus.add_service(self.menu)

        self.main_window.config(menu=self.menu.menu)

        self.atlas = Atlas(self.main_window)

        self.event_bus.add_service(self.atlas)

        self.combiner = Combiner(self.main_window)

        self.event_bus.add_service(self.combiner)

        self.nodes_catalog = NodeCatalog(self.main_window)
        self.event_bus.add_service(self.nodes_catalog)

        self.camera = Camera(self.main_window)
        self.event_bus.add_service(self.camera)

        self.traps = Traps(self.main_window)
        self.event_bus.add_service(self.traps)

        self.zernike = Zernike(self.main_window)
        self.event_bus.add_service(self.zernike)


        self.slm = SLM(self.main_window)

        self.event_bus.add_service(self.slm)

        #self.status = StatusBar(self.main_window)
        #self.status.grid(row=3, column=0, columnspan=4, sticky='ew')

        #self.event_bus.add_service(self.status)

    def run(self):
        self.main_window.mainloop()
