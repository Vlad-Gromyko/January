from tkinter import Menu

from application.core.events import Service


class TopMenu(Service):
    def __init__(self, main_window):
        super().__init__()
        self.name = 'Menu'

        self.menu = Menu(main_window)

        button1 = self.menu.add_cascade(label='Проект')
        button2 = self.menu.add_cascade(label='SLM')
        button3 = self.menu.add_cascade(label='Лазер')
        button4 = self.menu.add_cascade(label='Камера')
        button5 = self.menu.add_cascade(label='Оптическая система')
        button6 = self.menu.add_cascade(label='Диагностика')
        button7 = self.menu.add_cascade(label='Калибровка')


    def start_service(self, event):
        pass
