import customtkinter as ctk
import numpy as np

from application.core.events import Event
from application.core.services.node import INode
from application.widgets.maskwidget import MaskLabel

from application.core.utility.mask import Mask


class Node(INode):
    def __init__(self, config, editor, canvas, palette, x, y, text, theme, **kwargs):
        super().__init__(config, editor, canvas, palette, x, y, text, theme, **kwargs)

        self.add_enter_socket('', self.palette['SIGNAL'])
        self.add_enter_socket('Голограмма', self.palette['HOLOGRAM'])

        self.add_output_socket('', self.palette['SIGNAL'])

    def execute(self):
        arguments = self.get_func_inputs()

        self.event_bus.raise_event(Event('Set SLM Original', arguments['Голограмма']))

        self.output_sockets[''].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'SLM', 'slm'
