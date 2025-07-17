import numpy as np

from application.core.events import Event
from application.core.services.nodes.node import INode
from application.core.utility.mask import Mask
import customtkinter as ctk
import time
import numba


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

        starter = arguments['Стартер'].get_array()
        iters = arguments['Число Итераций']

        pixel = self.event_bus.get_field('slm pixel')

        width = int(self.event_bus.get_field('slm width'))
        height = int(self.event_bus.get_field('slm height'))

        focus = self.event_bus.get_field('optics focus')
        wave = self.event_bus.get_field('laser wavelength')

        x_mesh = np.linspace(-width * pixel / 2, width * pixel / 2, width)
        y_mesh = np.linspace(-height * pixel / 2, height * pixel / 2, height)

        x_mesh, y_mesh = np.meshgrid(x_mesh, y_mesh)

        phase = mega_HOTA(np.asarray(x), np.asarray(y), x_mesh, y_mesh, wave, focus, np.asarray(w),
                          starter, int(iters))

        self.output_sockets['Голограмма'].set_value(Mask(phase + np.pi))

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'SuperHota', 'traps'

    @staticmethod
    def possible_to_create():
        return True

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals


@numba.njit(fastmath=True, parallel=True)
def mega_HOTA(x_list, y_list, x_mesh, y_mesh, wave, focus, user_weights, initial_phase, iterations):
    num_traps = len(user_weights)
    v_list = np.zeros_like(user_weights, dtype=np.complex128)
    area = np.shape(initial_phase)[0] * np.shape(initial_phase)[1]
    phase = np.zeros_like(initial_phase)

    w_list = np.ones(num_traps)

    lattice = 2 * np.pi / wave / focus

    traps = np.empty((num_traps, x_mesh.shape[1], x_mesh.shape[0]))
    for i in numba.prange(num_traps):
        traps[i] = (lattice * (x_list[i] * x_mesh + y_list[i] * y_mesh)) % (2 * np.pi)

    for i in numba.prange(num_traps):
        v_list[i] = np.sum(np.exp(1j * (initial_phase - traps[i]))) / area

    anti_user_weights = 1 / user_weights

    for k in range(iterations):
        w_list_before = w_list.copy()
        avg = np.average(np.abs(v_list), weights=anti_user_weights)
        w_list = avg / np.abs(v_list) * user_weights * w_list_before

        weighted_phasors = (user_weights[:, None, None] * v_list[:, None, None] * w_list[:, None, None] /
                            np.abs(v_list)[:, None, None] * np.exp(1j * traps))
        summ = np.sum(weighted_phasors, axis=0)
        phase = np.angle(summ)

        for i in numba.prange(num_traps):
            v_list[i] = np.sum(np.exp(1j * (phase - traps[i]))) / area

    return phase
