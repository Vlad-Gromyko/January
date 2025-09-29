from application.core.services.nodes.node import INode
import numpy as np
import LightPipes as lp
import time

class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('', self.palette['CAMERA_SHOT'])
        self.add_enter_socket('Доля', self.palette['NUM'])

        self.add_output_socket('', self.palette['CAMERA_SHOT'])
        self.load_data = kwargs




    def execute(self):

        arguments = self.get_func_inputs()

        shot = arguments[''].copy()

        shot = np.where(shot > arguments['Доля'] * np.max(shot), shot, 0)
        shot = shot - np.min(shot)

        self.output_sockets[''].set_value(shot)

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Фильтр', 'camera'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
