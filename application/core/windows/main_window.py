import customtkinter as ctk
from application.core.events import Service


class MainWindow(Service, ctk.CTk):
    def __init__(self, *args, **kwargs):
        Service.__init__(self)
        ctk.CTk.__init__(self, *args, **kwargs)

        self.title('Hyperion')
        #self.geometry('1680x1050')
        self.iconify()

        self.events_reactions['Project Loaded'] = lambda event: self.deiconify()
        self.events_reactions['Load'] = lambda event: self.title(f'Hyperion  {event.get_value().split('/')[-1]}')
