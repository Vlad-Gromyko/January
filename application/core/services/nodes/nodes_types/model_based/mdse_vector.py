from application.core.events import Event
from application.core.services.nodes.node import INode
import customtkinter as ctk
import time
import numpy as np
import LightPipes as lp


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Моды', self.palette['vector1d'])
        self.add_enter_socket('Аберрации', self.palette['HOLOGRAM'])
        self.add_enter_socket('Бета', self.palette['NUM'])
        self.add_enter_socket('Число Пикселей', self.palette['NUM'])


        self.add_output_socket('MDSE 0', self.palette['NUM'])
        self.add_output_socket('Снимок 0', self.palette['CAMERA_SHOT'])
        self.add_output_socket('Тело Цикла', self.palette['SIGNAL'])
        self.add_output_socket('Индекс', self.palette['NUM'])
        self.add_output_socket('MDSE - MDSE0', self.palette['NUM'])
        self.add_output_socket('Снимок', self.palette['CAMERA_SHOT'])
        self.add_output_socket('Вектор', self.palette['vector1d'])


        self.load_data = kwargs

        self.strong_control = True
    def execute(self):
        arguments = self.get_func_inputs()

        vector = arguments['Моды']
        dim = len(vector)
        beta = arguments['Бета']
        aber = arguments['Аберрации']
        pixels = int(arguments['Число Пикселей'])

        holo = self.holo_box(aber.get_array())

        wave = self.event_bus.get_field('laser wavelength')
        gauss_waist = self.event_bus.get_field('laser waist')
        focus = self.event_bus.get_field('optics focus')
        slm_grid_dim = self.event_bus.get_field('slm width')
        slm_grid_size = self.event_bus.get_field('slm width') * self.event_bus.get_field('slm pixel')

        field = lp.Begin(slm_grid_size, wave,
                              slm_grid_dim)

        field = lp.GaussBeam(field, gauss_waist)

        camera_grid_dim = pixels
        camera_grid_size = camera_grid_dim * float(self.config['CAMERA']['modeling_pixel_UM']) * 10 ** (
            -6)

        field = lp.SubPhase(field, holo)
        field = lp.Lens(field, focus)
        field = lp.Forvard(field, focus)

        field = lp.Interpol(field, camera_grid_size,
                            camera_grid_dim)
        shot = lp.Intensity(field)

        w, h = np.shape(shot)

        x = np.linspace(-h / 2, h / 2, h)
        y = np.linspace(-w / 2, w / 2, w)
        x, y = np.meshgrid(x, y)

        signal_intensity = np.sum(shot * (x ** 2 + y ** 2))
        summ_intensity = np.sum(shot)

        m0 = signal_intensity / summ_intensity

        self.output_sockets['MDSE 0'].set_value(m0)
        self.output_sockets['Снимок 0'].set_value(shot)

        result = []

        for i in range(dim):
            self.output_sockets['Тело Цикла'].set_value(None)

            self.output_sockets['Индекс'].set_value(i)

            holo = aber + vector[i] * beta
            holo = self.holo_box(holo.get_array())

            wave = self.event_bus.get_field('laser wavelength')
            gauss_waist = self.event_bus.get_field('laser waist')
            focus = self.event_bus.get_field('optics focus')
            slm_grid_dim = self.event_bus.get_field('slm width')
            slm_grid_size = self.event_bus.get_field('slm width') * self.event_bus.get_field('slm pixel')

            field = lp.Begin(slm_grid_size, wave,
                             slm_grid_dim)

            field = lp.GaussBeam(field, gauss_waist)

            camera_grid_dim = pixels
            camera_grid_size = camera_grid_dim * float(self.config['CAMERA']['modeling_pixel_UM']) * 10 ** (
                -6)

            field = lp.SubPhase(field, holo)
            field = lp.Lens(field, focus)
            field = lp.Forvard(field, focus)

            field = lp.Interpol(field, camera_grid_size,
                                camera_grid_dim)
            shot = lp.Intensity(field)

            w, h = np.shape(shot)

            x = np.linspace(-h / 2, h / 2, h)
            y = np.linspace(-w / 2, w / 2, w)
            x, y = np.meshgrid(x, y)

            signal_intensity = np.sum(shot * (x ** 2 + y ** 2))
            summ_intensity = np.sum(shot)

            self.output_sockets['MDSE - MDSE0'].set_value(m0 - signal_intensity / summ_intensity)
            self.output_sockets['Снимок'].set_value(shot)

            self.output_sockets['Тело Цикла'].set_value(True)

            result.append(m0 - signal_intensity / summ_intensity)

        self.output_sockets['Вектор'].set_value(result)

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'MDSE Vector Model', 'model'

    @staticmethod
    def possible_to_create():
        return True

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals

    @staticmethod
    def holo_box(holo):
        rows, cols = holo.shape

        size = max(rows, cols)

        square_array = np.zeros((size, size), dtype=holo.dtype)

        row_offset = (size - rows) // 2
        col_offset = (size - cols) // 2

        square_array[row_offset:row_offset + rows, col_offset:col_offset + cols] = holo

        return square_array