import numpy as np

from application.core.events import Event
from application.core.services.nodes.node import INode
import cv2
import time


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id
        self.add_enter_socket('k', self.palette['NUM'])
        self.add_enter_socket('Число кадров', self.palette['NUM'])
        self.add_enter_socket('Порт', self.palette['NUM'])

        self.add_output_socket('Снимок', self.palette['CAMERA_SHOT'])

        self.load_data = kwargs

    def execute(self):
        arguments = self.get_func_inputs()
        shots = []

        k = arguments['k']

        fit = None

        cap = cv2.VideoCapture(int(arguments['Порт']), cv2.CAP_DSHOW)
        for i in range(int(arguments['Число кадров'])):
            ret, frame = cap.read()
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            if fit is None:
                fit = frame
            else:
                frame = fit * k + frame * (1 - k)
                fit = frame

            shots.append(frame)

        cap.release()

        shot = np.median(shots, axis=0)

        self.output_sockets['Снимок'].set_value(shot)

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, ('Адаптивный медианный снимок'), 'camera'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals

    def saves_dict(self):
        enters = dict()
        for item in self.enter_sockets.values():
            enters[item.name + '_enter'] = item.get_value()

        outputs = dict()
        for item in self.output_sockets.values():
            outputs[item.name + '_output'] = item.get_value()

        return {**enters, **outputs}
