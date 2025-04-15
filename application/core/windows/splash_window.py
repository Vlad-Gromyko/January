import customtkinter as ctk
from application.core.events import Service, Event
from PIL import Image
import os, random


class SplashWindow(Service, ctk.CTkToplevel):
    def __init__(self):
        Service.__init__(self)
        ctk.CTkToplevel.__init__(self)
        self.name = 'Splash'
        self.title('Splash')
        path = r"resources/splashes/"
        image = Image.open(path + random.choice(os.listdir(path)))
        self.label = ctk.CTkLabel(self, image=ctk.CTkImage(light_image=image, size=(image.width, image.height)), text='')
        self.label.grid()

        self.geometry(f'{image.width}x{image.height}')

        self.events_reactions['Load'] = lambda event: self.show_splash()
        self.events_reactions['Project Loaded'] = lambda event: self.withdraw()

        self.events_reactions['Show Splash'] = lambda event: self.show_splash()
        self.events_reactions['Hide Splash'] = lambda event: self.withdraw()

        self.withdraw()
        self.overrideredirect(1)
        self.attributes('-topmost', True)


    def show_splash(self):

        self.deiconify()
        self.update()

    def start_service(self, event):
        pass
