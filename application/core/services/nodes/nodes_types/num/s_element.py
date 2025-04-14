import numpy as np

from application.core.events import Event
from application.core.services.nodes.node import INode


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('N', self.palette['HOLOGRAM'])
        self.add_enter_socket('M', self.palette['HOLOGRAM'])

        self.add_output_socket('Значение', self.palette['NUM'])
        self.load_data = kwargs
    def execute(self):
        arguments = self.get_func_inputs()

        holo1 = arguments['N'].get_array()
        holo2 = arguments['M'].get_array()

        value = np.sum(np.diff(holo1, axis=0, append=0) * np.diff(holo2, axis=0, append=0) + np.diff(holo1, axis=1, append=0) * np.diff(holo2, axis=1, append=0))
        value = value / np.shape(holo1)[0] / np.shape(holo1)[1]


        self.output_sockets['Значение'].set_value(value)
        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'S (N, M)', 'math'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
