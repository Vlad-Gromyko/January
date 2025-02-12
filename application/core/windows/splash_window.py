import customtkinter as ctk
from application.core.events import Service, Event


class SplashWindow(Service, ctk.CTkToplevel):
    def __init__(self):
        Service.__init__(self)
        ctk.CTkToplevel.__init__(self, fg_color='#F00')
        self.name = 'Splash'
        self.title('Splash')

        self.label = ctk.CTkLabel(self, text='ЭТООООО СПЛЭЭЭЭШ')
        self.label.grid(padx=50, pady=50)

        self.events_reactions['Load'] = lambda event: self.show_splash()
        self.events_reactions['Project Loaded'] = lambda event: self.destroy()

        self.iconify()


    def show_splash(self):
        self.deiconify()
        self.update()

    def start_service(self, event):
        pass
