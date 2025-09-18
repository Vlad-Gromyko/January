import numpy
import numpy as np
import customtkinter as ctk
from application.core.services.nodes.node import INode

from application.core.utility.mask import Mask


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Моды', self.palette['vector1d'])
        self.add_enter_socket('Шаг', self.palette['NUM'])

        self.add_enter_socket('Метрика', self.palette['NUM'])

        self.add_output_socket('Индекс', self.palette['NUM'])

        self.add_output_socket('', self.palette['SIGNAL'])
        self.add_output_socket('Голограмма', self.palette['HOLOGRAM'])

        self.add_output_socket('M', self.palette['vector1d'])

        self.load_data = kwargs
        self.strong_control = True

    def execute(self):
        arguments = self.get_func_inputs()

        modes = arguments['Моды']
        step = arguments['Шаг']

        self.output_sockets['Индекс'].set_value(0)
        self.output_sockets['Голограмма'].set_value(Mask(np.zeros_like(modes[0])))
        self.output_sockets[''].set_value(True)

        arguments = self.get_func_inputs()
        m_0 = arguments['Метрика']

        m_vector = []

        for i in range(len(modes)):
            self.output_sockets['Индекс'].set_value(i + 1)
            self.output_sockets['Голограмма'].set_value(Mask(modes[i] * step))
            self.output_sockets[''].set_value(True)

            arguments = self.get_func_inputs()
            metric = arguments['Метрика']

            m_vector.append(m_0 - metric)
            print(m_0 - metric)

        self.output_sockets['M'].set_value(m_vector)

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'M-Матрица', 'model'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
