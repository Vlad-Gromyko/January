from application.core.events import Event
from application.core.services.nodes.node import INode

import numpy as np


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id


        self.add_enter_socket('Снимок', self.palette['CAMERA_SHOT'])

        self.add_output_socket('Пересвет', self.palette['BOOL'])


        self.load_data = kwargs

    def execute(self):
        arguments = self.get_func_inputs()

        shot = arguments['Снимок']
        result = False
        if np.max(shot) == 254 or np.max(shot) == 255:
            result = True

        self.output_sockets['Пересвет'].set_value(result)


        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Пересвет', 'camera'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals

    def saves_dict(self):
        enters = dict()
        for item in self.enter_sockets.values():
            enters[item.name + '_enter'] = item.get_value()

        outputs = dict()
        for item in self.output_sockets.values():
            outputs[item.name + '_output'] = item.get_value()

        return {**enters, **outputs}