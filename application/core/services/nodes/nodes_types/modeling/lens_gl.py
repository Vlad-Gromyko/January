from application.core.services.nodes.node import INode
import numpy as np
import LightPipes as lp
import time

class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Голограмма', self.palette['HOLOGRAM'])
        self.add_enter_socket('Число пикселей', self.palette['NUM'])
        self.add_enter_socket('p', self.palette['NUM'])
        self.add_enter_socket('l', self.palette['NUM'])

        self.add_output_socket('Интенсивность', self.palette['CAMERA_SHOT'])
        self.load_data = kwargs
        self.field = None
        self.wave = None
        self.focus = None
        self.gauss_waist = None

        self.slm_grid_size = None
        self.slm_grid_dim = None

        self.camera_grid_size = None
        self.camera_grid_dim = None

        self.p = None
        self.l = None

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
        start_time = time.time()
        arguments = self.get_func_inputs()

        holo = self.holo_box(arguments['Голограмма'].get_array())

        wave = self.event_bus.get_field('laser wavelength')
        gauss_waist = self.event_bus.get_field('laser waist')
        focus = self.event_bus.get_field('optics focus')
        slm_grid_dim = self.event_bus.get_field('slm width')

        if wave != self.wave or gauss_waist != self.gauss_waist or focus != self.focus or slm_grid_dim != self.slm_grid_dim:
            print('lens')
            self.wave = wave
            self.gauss_waist = gauss_waist
            self.focus = focus
            self.slm_grid_dim = slm_grid_dim
            self.slm_grid_size = self.slm_grid_dim * self.event_bus.get_field('slm pixel')

            self.field = lp.Begin(self.slm_grid_size, self.wave,
                                  self.slm_grid_dim)

        p = arguments['p']
        l = arguments['l']
        self.field = lp.GaussLaguerre(self.field, self.gauss_waist, p, l)
        self.camera_grid_dim = slm_grid_dim
        self.camera_grid_dim = int(arguments['Число пикселей'])
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
        return Node, 'Линза ГЛ', 'camera'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
