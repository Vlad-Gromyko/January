import numpy as np

from application.core.events import Event
from application.core.services.nodes.node import INode


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id


        self.add_enter_socket('Снимок', self.palette['CAMERA_SHOT'])
        self.add_output_socket('Значение', self.palette['NUM'])

        self.load_data = kwargs

    def execute(self):
        arguments = self.get_func_inputs()

        shot = arguments['Снимок']

        w, h = np.shape(shot)

        x = np.linspace(-h* float(self.config['CAMERA']['modeling_pixel_UM']) * 10 ** (
                -6)/2, h* float(self.config['CAMERA']['modeling_pixel_UM']) * 10 ** (
                -6)/2, h)
        y = np.linspace(-w* float(self.config['CAMERA']['modeling_pixel_UM']) * 10 ** (
                -6)/2, w* float(self.config['CAMERA']['modeling_pixel_UM']) * 10 ** (
                -6)/2, w)
        x, y = np.meshgrid(x, y)

        signal_intensity = np.sum(shot * (x ** 2 + y ** 2))
        summ_intensity = np.sum(shot)

        self.output_sockets['Значение'].set_value(signal_intensity / summ_intensity)
        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'MDSE', 'model'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
