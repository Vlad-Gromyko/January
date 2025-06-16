import customtkinter as ctk
import numpy as np

from application.core.events import Event
from application.core.services.nodes.node import INode


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('', self.palette['CAMERA_SHOT'])

        self.add_output_socket('', self.palette['NUM'])


        self.load_data = kwargs
        self.strong_control = False

    def execute(self):
        arguments = self.get_func_inputs()

        shot = arguments['']

        w, h = np.shape(shot)

        x = np.linspace(-h / 2, h / 2, h)
        y = np.linspace(-w / 2, w / 2, w)
        x, y = np.meshgrid(x, y)

        sigma_x = np.sum(x*x*shot)
        sigma_y = np.sum(y*y*shot)

        print(sigma_x, sigma_x)


        self.output_sockets[''].set_value(np.abs(sigma_x - sigma_y))

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Эллиптичность', 'Metric'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
