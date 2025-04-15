from application.core.events import Event
from application.core.services.nodes.node import INode
from application.core.utility.mask import Mask
import LightPipes as lp
import numpy as np


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Амплитуда (\u03BB)', self.palette['NUM'])

        self.add_enter_socket('Номер', self.palette['NUM'])

        self.add_output_socket('Голограмма', self.palette['HOLOGRAM'])
        self.load_data = kwargs

    def execute(self):
        arguments = self.get_func_inputs()

        num = arguments['Номер'] +1

        wavelength = self.event_bus.get_field('laser wavelength')
        slm_grid_dim = self.event_bus.get_field('slm width')
        slm_grid_size = self.event_bus.get_field('slm width') * self.event_bus.get_field('slm pixel')

        (nz, mz) = lp.noll_to_zern(num)

        field = lp.Begin(slm_grid_size, wavelength, slm_grid_dim)
        field = lp.Zernike(field, nz, mz, slm_grid_size / 2, A=arguments['Амплитуда (\u03BB)'], norm=True,
                           units='lam')

        holo = lp.Phase(field)

        pad = np.min(holo)

        if pad< 0:
            holo = (holo + pad)
        holo = holo % (2 * np.pi)

        self.output_sockets['Голограмма'].set_value(Mask(holo))
        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Цернике - NRMS', 'hologram'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals

    @staticmethod
    def holo_cut(holo):
        rows, cols = holo.shape

        size = max(rows, cols)

        result = holo[:, (max(rows, cols) - min(rows, cols)) // 2: size - (max(rows, cols) - min(rows, cols)) // 2]

        return result
