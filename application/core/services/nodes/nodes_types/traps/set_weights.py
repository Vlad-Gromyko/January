import numpy as np

from application.core.events import Event
from application.core.services.nodes.node import INode
import customtkinter as ctk
import time
from application.core.utility.mask import Mask


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Вектор весов', self.palette['vector1d'])

        self.load_data = kwargs

    def execute(self):
        arguments = self.get_func_inputs()

        weights = arguments['Вектор весов']

        self.event_bus.raise_event(Event('Set Weight Traps', weights))


        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Установить Веса', 'traps'

    @staticmethod
    def possible_to_create():
        return True

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
