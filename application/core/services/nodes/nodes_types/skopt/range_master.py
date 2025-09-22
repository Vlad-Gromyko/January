import numpy
import numpy as np
import customtkinter as ctk
from application.core.services.nodes.node import INode


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('', self.palette['vector1d'])

        self.add_output_socket('MIN', self.palette['vector1d'])
        self.add_output_socket('MAX', self.palette['vector1d'])

        self.load_data = kwargs
        self.strong_control = False

    def execute(self):
        arguments = self.get_func_inputs()

        minimums = np.min(np.asarray(arguments['']), axis=0)
        maximums = np.max(np.asarray(arguments['']), axis=0)

        self.output_sockets['MIN'].set_value(minimums)
        self.output_sockets['MAX'].set_value(maximums)

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Range', 'strategy'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
