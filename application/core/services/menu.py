import tkinter
from cProfile import label

from tkinter import Menu

from application.core.events import Service, Event


class TopMenu(Service):
    def __init__(self, main_window):
        super().__init__()
        self.name = 'Menu'


        self.menu = Menu(main_window)

        file_menu = Menu(tearoff=0)
        file_menu.add_command(label="New")
        file_menu.add_command(label="Save")
        file_menu.add_command(label="Open")
        file_menu.add_command(label="Exit")

        slm_menu=Menu(tearoff=0)



        slm_menu.add_command(label='Трансляция', command=lambda:self.show_callback('SLM'))
        slm_menu.add_command(label='Калибровка')

        camera_menu = Menu(tearoff=0)


        camera_menu.add_command(label='Камера', command=lambda:self.show_callback('Camera'))

        traps_menu = Menu()

        traps_menu.add_command(label='Ловушки', command=lambda : self.show_callback('Traps'))

        nodes_menu = Menu(tearoff=0)
        nodes_menu.add_command(label='Каталог Нод', command=lambda:self.show_callback('Nodes'))

        holo_menu = Menu(tearoff=0)
        holo_menu.add_command(label='Цернике', command=lambda:self.show_callback('Zernike'))

        order_menu = Menu(tearoff=0)
        order_menu.add_command(label='Атлас', command=lambda:self.show_callback('Atlas'))
        order_menu.add_command(label='Сумматор', command=lambda:self.show_callback('Combiner'))

        self.menu.add_cascade(label='Проект', menu=file_menu)
        self.menu.add_cascade(label='SLM', menu=slm_menu)
        self.menu.add_cascade(label='Камера', menu=camera_menu)
        self.menu.add_cascade(label='Голограммы', menu=holo_menu)
        self.menu.add_cascade(label='Ноды', menu=nodes_menu)
        self.menu.add_cascade(label='Очереди', menu=order_menu)
        self.menu.add_cascade(label='Ловушки', menu=traps_menu)

    def show_callback(self, name):
            self.event_bus.raise_event(Event('Show/Hide Service ' + name))


    def start_service(self, event):
        pass
