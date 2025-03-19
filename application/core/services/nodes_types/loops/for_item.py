import customtkinter as ctk
import numpy as np

from application.core.events import Event
from application.core.services.node import INode
from application.widgets.maskwidget import MaskLabel

from application.core.utility.mask import Mask


class Node(INode):
    def __init__(self, config, editor, canvas, palette, x, y, **kwargs):
        super().__init__(config, editor, canvas, palette, x, y, text='For Item', theme='hologram', **kwargs)

        self.add_enter_socket('', self.palette['SIGNAL'])

        self.add_enter_socket('Контейнер', self.palette['ANY'])


        self.add_output_socket('Тело Цикла', self.palette['SIGNAL'])
        self.add_output_socket('Индекс', self.palette['NUM'])
        self.add_output_socket('Объект', self.palette['ANY'])

        self.add_output_socket('Завершение', self.palette['SIGNAL'])

    def execute(self):
        arguments = self.get_func_inputs()


        for counter, item in enumerate(arguments['Контейнер']):
            self.output_sockets['Тело Цикла'].set_value(None)

            self.output_sockets['Индекс'].set_value(counter)

            self.output_sockets['Объект'].set_value(item)

            self.output_sockets['Тело Цикла'].set_value(True)

        self.output_sockets['Завершение'].set_value(True)
