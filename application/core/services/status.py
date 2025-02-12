import customtkinter as ctk

from application.core.events import Service


class StatusBar(Service, ctk.CTkFrame):
    def __init__(self, master):
        Service.__init__(self)
        ctk.CTkFrame.__init__(self, master)
        self.name = 'StatusBar'


        self.label = ctk.CTkLabel(self, text='Статус:  Успешный запуск')
        self.label.grid(row=0, column=0, padx=5, sticky='w')

        self.progress = ctk.CTkProgressBar(self, orientation='horizontal')
        self.progress.grid(row=0, column=1, sticky='we', padx=5)
        self.progress.set(0)

        self.grid_columnconfigure((0, 1), weight=1)

        self.events_reactions['Status'] = lambda event: self.new_status(event)



    def start_service(self, event):
        pass

    def new_status(self, event):
        data = event.get_value()
        if 'status' in data.keys():
            self.label.configure(text=f'Статус:  {data['status']}')
        if 'value' in data.keys():
            self.progress.set(data['value']/data['max'])