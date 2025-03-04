import customtkinter as ctk
from application.core.events import Service, Event

from tkinterdnd2 import TkinterDnD, DND_ALL


class MainWindow(Service, ctk.CTk):
    def __init__(self, *args, **kwargs):
        Service.__init__(self)
        ctk.CTk.__init__(self, *args, **kwargs)

        self.TkdndVersion = TkinterDnD._require(self)

        self.drop_target_register(DND_ALL)
        self.dnd_bind("<<DropEnter>>", self.drop)
        self.dnd_bind("<<DropLeave>>", self.drop_fall)

        self.title('Hyperion')
        self.geometry('1680x1050')
        self.iconify()

        self.events_reactions['Project Loaded'] = lambda event: self.deiconify()
        self.events_reactions['Load'] = lambda event: self.title(f'Hyperion  {event.get_value().split('/')[-1]}')

    def drop(self, event):
        self.event_bus.raise_event(Event('Drop Start'))

    def drop_fall(self, event):
        self.event_bus.raise_event(Event('Drop End'))
