import numpy as np

from application.core.services.nodes.node import INode

import LightPipes as lp


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id


        self.add_enter_socket('S', self.palette['vector2d'])
        self.add_enter_socket('M', self.palette['vector2d'])
        self.add_enter_socket('Beta', self.palette['NUM'])


        self.add_output_socket('Вектор', self.palette['vector1d'])


        self.load_data = kwargs



    def execute(self):
        arguments = self.get_func_inputs()

        s = np.asarray(arguments('S'))
        m = np.asarray(arguments('M'))
        beta = arguments('Beta')
        sm = s.diagonal()
        c = 1 / 4 /np.pi**2

        vector = np.dot(np.linalg.inv(s), m) / 2 / c / beta - beta * np.dot(np.linalg.inv(s), sm)/2

        self.output_sockets['Вектор'].set_value(vector)
        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Model-Based', 'math'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals