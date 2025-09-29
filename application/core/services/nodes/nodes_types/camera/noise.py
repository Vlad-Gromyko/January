from application.core.services.nodes.node import INode
import numpy as np
import LightPipes as lp
import time

from perlin_noise import PerlinNoise

class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('', self.palette['CAMERA_SHOT'])

        self.add_enter_socket('Октавы', self.palette['NUM'])
        self.add_enter_socket('Сид', self.palette['NUM'])
        self.add_enter_socket('Глубина', self.palette['NUM'])

        self.add_output_socket('', self.palette['CAMERA_SHOT'])
        self.load_data = kwargs




    def execute(self):

        arguments = self.get_func_inputs()

        noise = PerlinNoise(octaves=arguments['Октавы'], seed=arguments['Сид'])
        ypix, xpix = np.shape(arguments[''])
        shot = [[noise([i/xpix, j/ypix]) for j in range(xpix)] for i in range(ypix)]

        shot = np.asarray(shot)

        shot = np.abs(shot)

        shot = shot - np.min(shot)

        shot = np.ones_like(shot) - shot * arguments['Глубина']

        self.output_sockets[''].set_value(shot)

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Перлин', 'Noise'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
