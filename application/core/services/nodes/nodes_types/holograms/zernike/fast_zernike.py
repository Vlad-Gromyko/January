from application.core.services.nodes.node import INode
import numpy as np
from application.core.utility.fast_zernike import zernike_by_number
from application.core.utility.mask import Mask
import time


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Амплитуда', self.palette['NUM'])
        self.add_enter_socket('Номер', self.palette['NUM'])

        self.add_output_socket('', self.palette['HOLOGRAM'])
        self.load_data = kwargs

        self.slm_width = None
        self.slm_height = None
        self.slm_pixel = None

        self.phi = None
        self.rho = None

    def execute(self):
        start_time = time.time()
        arguments = self.get_func_inputs()

        num = arguments['Номер']
        amp = arguments['Амплитуда']

        width = self.event_bus.get_field('slm width')
        height = self.event_bus.get_field('slm height')
        pixel = self.event_bus.get_field('slm pixel')
        if self.slm_width != width or self.height != height or self.slm_pixel != pixel:
            self.slm_width = width
            self.slm_height = height
            self.slm_pixel = pixel
            x = np.linspace(-self.slm_width * self.slm_pixel / 2, self.slm_width * self.slm_pixel / 2, self.slm_width)
            y = np.linspace(-self.slm_height * self.slm_pixel / 2, self.slm_height * self.slm_pixel / 2, height)

            x, y = np.meshgrid(x, y)

            self.rho = np.sqrt(x ** 2 + y ** 2)

            phi = np.arctan2(y, x)
            phi = phi + np.min(phi)

            self.phi = np.flip(phi, 1)

        holo = zernike_by_number(num, self.rho, self.phi)


        self.output_sockets[''].set_value(Mask(holo) * amp)
        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Быстрый', 'Zernike'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
