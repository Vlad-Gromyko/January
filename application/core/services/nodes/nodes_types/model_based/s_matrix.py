import numpy as np

from application.core.events import Event
from application.core.services.nodes.node import INode

import matplotlib.pyplot as plt


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Моды', self.palette['vector1d'])
        self.load_data = kwargs
        self.add_output_socket('', self.palette['vector2d'])
        self.add_output_socket('inv(S)', self.palette['vector2d'])

        self.strong_control = True

    def execute(self):
        arguments = self.get_func_inputs()

        vector = arguments['Моды'].copy()

        dim = len(vector)


        result = [[np.sum(
            np.diff(vector[j], axis=0, append=0) * np.diff(vector[i], axis=0, append=0) + np.diff(vector[i], axis=1,
                                                                                          append=0) * np.diff(
                vector[j], axis=1, append=0)) for j in range(dim)] for i in range(dim)]


        self.output_sockets[''].set_value(np.asarray(result))

        plt.imshow(np.linalg.inv(np.asarray(result)))
        plt.show()

        self.output_sockets['inv(S)'].set_value(np.linalg.inv(np.asarray(result)))
        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'S-Матрица', 'model'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
