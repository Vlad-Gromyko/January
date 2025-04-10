import numpy as np

from application.core.services.nodes.node import INode

import LightPipes as lp


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id


        self.add_enter_socket('Голограмма', self.palette['HOLOGRAM'])

        self.add_output_socket('Интенсивность', self.palette['CAMERA_SHOT'])

        self.field = None
        self.wave = None
        self.focus = None
        self.gauss_waist = None

        self.slm_grid_size = None
        self.slm_grid_dim = None

        self.camera_grid_size = None
        self.camera_grid_dim = None

    @staticmethod
    def holo_box(holo):
        rows, cols = holo.shape

        size = max(rows, cols)

        square_array = np.zeros((size, size), dtype=holo.dtype)

        row_offset = (size - rows) // 2
        col_offset = (size - cols) // 2

        square_array[row_offset:row_offset + rows, col_offset:col_offset + cols] = holo

        return square_array

    def execute(self):
        arguments = self.get_func_inputs()

        holo = self.holo_box(arguments['Голограмма'].get_array())
        if self.field is None:
            self.wave = float(self.config['LASER']['wavelength_NM']) * 10 ** (-9)
            self.gauss_waist = float(self.config['LASER']['waist_mm']) * 10 ** (-3)
            self.focus = float(self.config['LENS']['Focus_MM']) * 10 ** (-3)

            self.slm_grid_dim = int(self.config['SLM']['WIDTH'])
            self.slm_grid_size = self.slm_grid_dim * float(self.config['SLM']['PIXEL_IN_UM']) * 10 ** (-6)

            self.field = lp.Begin(self.slm_grid_size, self.wave,
                                  self.slm_grid_dim)

            self.field = lp.GaussBeam(self.field, self.gauss_waist)

            self.camera_grid_dim = int(self.config['CAMERA']['modeling_width'])
            self.camera_grid_size = self.camera_grid_dim * float(self.config['CAMERA']['modeling_pixel_UM']) * 10 ** (
                -6)

        field = lp.SubPhase(self.field, holo)
        field = lp.Lens(field, self.focus)
        field = lp.Forvard(field, self.focus)

        field = lp.Interpol(field, self.camera_grid_size,
                            self.camera_grid_dim)
        result = lp.Intensity(field)

        self.output_sockets['Интенсивность'].set_value(result)
        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Линза', 'camera'

    def prepare_save_spec(self):
        return __file__, self.x, self.y, {}, self.special_id, self.with_signals