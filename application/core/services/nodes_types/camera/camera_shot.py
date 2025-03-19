import customtkinter as ctk
import numpy as np

from application.core.events import Event
from application.core.services.node import INode
from application.widgets.maskwidget import MaskLabel

from application.core.utility.mask import Mask

import time


class Node(INode):
    def __init__(self, config, editor, canvas, palette, x, y, text, theme, **kwargs):
        super().__init__(config, editor, canvas, palette, x, y, text=text, theme=theme, **kwargs)

        self.add_enter_socket('Фон', self.palette['SIGNAL'])
        self.add_enter_socket('Снимок', self.palette['SIGNAL'])
        self.add_output_socket('', self.palette['SIGNAL'])

        self.add_output_socket('Снимок', self.palette['CAMERA_SHOT'])
        self.add_output_socket('Фон', self.palette['CAMERA_SHOT'])
        self.add_output_socket('Снимок - Фон', self.palette['CAMERA_SHOT'])


    def execute(self):
        arguments = self.get_func_inputs()

        if arguments['Снимок'] is not None:
            self.event_bus.raise_event(Event('Take Shot'))
        else:
            self.event_bus.raise_event(Event('Take Back'))

        back = self.event_bus.get_field('Back')
        shot = self.event_bus.get_field('Shot')
        shot_back = self.event_bus.get_field('Shot - Back')


        self.output_sockets['Фон'].set_value(back)
        self.output_sockets['Снимок'].set_value(shot)
        self.output_sockets['Снимок - Фон'].set_value(shot_back)

        self.output_sockets[''].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Камера', 'camera'