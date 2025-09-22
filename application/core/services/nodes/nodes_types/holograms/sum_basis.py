
from application.core.events import Event
from application.core.services.nodes.node import INode
import customtkinter as ctk
import time
from functools import reduce
import numpy as np
import matplotlib.pyplot as plt

from application.core.utility.mask import Mask


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Базис', self.palette['vector1d'])
        self.add_enter_socket('Вектор', self.palette['vector1d'])

        self.add_output_socket('', self.palette['HOLOGRAM'])

        self.load_data = kwargs

        self.strong_control = False
    def execute(self):
        timer = time.time()
        arguments = self.get_func_inputs()

        basis = arguments['Базис'].copy()

        basis = np.asarray(basis)

        vector = arguments['Вектор'].copy()

        vector = np.asarray(vector)

        result = np.angle(np.exp(1j * np.sum(basis * vector[:, np.newaxis, np.newaxis], axis=0)))
        #result = np.sum(basis * vector[:, np.newaxis, np.newaxis], axis=0)

        floor = np.min(result)

        if floor < 0:
            result = result - floor

        result = result % (2 * np.pi)



        mask = Mask(result)

        self.output_sockets[''].set_value(mask)


        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'SUM Basis', 'Container'

    @staticmethod
    def possible_to_create():
        return True

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
