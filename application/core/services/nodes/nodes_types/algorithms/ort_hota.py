import numba
import numpy as np

from application.core.events import Event
from application.core.services.nodes.node import INode
from application.core.utility.mask import Mask
import customtkinter as ctk
import time
import numba as nb


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Ловушки', self.palette['vector1d'])

        self.add_enter_socket('Стартер', self.palette['HOLOGRAM'])
        self.add_enter_socket('Число Итераций', self.palette['NUM'])

        self.add_output_socket('Голограмма', self.palette['HOLOGRAM'])
        self.load_data = kwargs

        self.strong_control = True

    def execute(self):
        arguments = self.get_func_inputs()

        traps = arguments['Ловушки']

        x = []
        y = []
        z = []
        w = []
        for item in traps:
            x.append(item[0])
            y.append(item[1])
            z.append(item[2])
            w.append(item[3])

        starter = arguments['Стартер']
        iters = arguments['Число Итераций']

        pixel = self.event_bus.get_field('slm pixel')

        width = int(self.event_bus.get_field('slm width'))
        height = int(self.event_bus.get_field('slm height'))

        focus = self.event_bus.get_field('optics focus')
        wave = self.event_bus.get_field('laser wavelength')

        x_mesh = np.linspace(-width * pixel / 2, width * pixel / 2, width)
        y_mesh = np.linspace(-height * pixel / 2, height * pixel / 2, height)

        x_mesh, y_mesh = np.meshgrid(x_mesh, y_mesh)
        x_mesh, y_mesh = x_mesh * 2 * np.pi / wave / focus, y_mesh * 2 * np.pi / wave / focus

        timer = time.time()

        phase = mega_HOTA_optimized(np.asarray(x), np.asarray(y), x_mesh, y_mesh, np.asarray(w),
                                    starter.get_array(), int(iters))

        print('TIMER  ', timer - time.time())

        self.output_sockets['Голограмма'].set_value(Mask(phase + np.pi))

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'ort_Hota', 'traps'

    @staticmethod
    def possible_to_create():
        return True

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals


@nb.njit(fastmath=True, parallel=True)
def mega_HOTA_optimized(x_list, y_list, ort_x, ort_y, user_weights, initial_phase, iterations):
    traps_num = len(x_list)
    area = ort_x.shape[0] * ort_x.shape[1]
    v_values = np.zeros_like(x_list, dtype='complex128')

    phase = np.zeros_like(initial_phase)

    w_list = np.ones(traps_num)

    for i in nb.prange(traps_num):
        v_values[i] = np.sum((np.exp(1j * ( initial_phase - ort_x * x_list[i] - ort_y * y_list[i]))))/ area

    anti_user_weights = 1 / user_weights

    for i in range(iterations):
        v_norms = np.abs(v_values)
        avg = np.average(v_norms, weights=anti_user_weights)

        w_list = avg / v_norms * user_weights * w_list


        summ_real = np.zeros_like(initial_phase, dtype=np.float64)
        summ_imag = np.zeros_like(initial_phase, dtype=np.float64)

        for ip in range(traps_num):
            trap = x_list[ip] * ort_x + y_list[ip] * ort_y

            cos_t = np.cos(trap)
            sin_t = np.sin(trap)

            weight = user_weights[ip] * v_values[ip] * w_list[ip] / v_norms[ip]
            wr = weight.real
            wi = weight.imag

            summ_real += cos_t * wr - sin_t * wi
            summ_imag += cos_t * wi + sin_t * wr

        phase = np.arctan2(summ_imag, summ_real)

        for iv in nb.prange(traps_num):
            v_values[iv] = np.sum((np.exp(1j * (phase - ort_x * x_list[iv] - ort_y * y_list[iv])))) / area

    return phase



