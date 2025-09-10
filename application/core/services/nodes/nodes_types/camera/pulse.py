import customtkinter as ctk
import os
from application.core.events import Event
from application.core.services.nodes.node import INode
from tkinter.filedialog import askdirectory
from matplotlib import cm
from PIL import Image
import cv2
import numpy as np


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Порт', self.palette['NUM'])
        self.add_enter_socket('Число Кадров', self.palette['NUM'])
        self.add_enter_socket('Порог', self.palette['NUM'])

        self.add_output_socket('Снимок', self.palette['CAMERA_SHOT'], )

        self.load_data = kwargs
        self.strong_control = False

        self.widget_width = 300
        self.widget_height = 40
        frame_widgets = ctk.CTkFrame(self.canvas, width=self.widget_width, height=self.widget_height)
        self.frame_IDs['widgets'] = self.canvas.create_window(self.x, self.y, window=frame_widgets,
                                                              anchor=ctk.NW, width=self.widget_width,
                                                              height=self.widget_height)

        values = ['Ср.Арифметическое', 'Экс.Сглаживание','Медиана']

        self.combo = ctk.CTkComboBox(frame_widgets, values=values, width=150)
        self.combo.set('Экс.Сглаживание')
        self.combo.grid(row=0)

        self.entry_alpha = ctk.CTkEntry(frame_widgets)
        self.entry_alpha.insert(0, '0.1')
        self.entry_alpha.grid(row=0, column=1)


    def execute(self):
        arguments = self.get_func_inputs()

        shots = []
        alpha = float(self.entry_alpha.get())

        cap = cv2.VideoCapture(int(arguments['Порт']), cv2.CAP_DSHOW)
        for i in range(int(arguments['Число Кадров'])):

            ret, frame = cap.read()

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            frame = np.where(frame > int(arguments['Порог']), frame, 0)
            frame = frame - np.min(frame)
            frame = frame / np.sum(frame)
            shots.append(frame)

        cap.release()
        result_shot = shots[0]
        if self.combo.get() == 'Ср.Арифметическое':
            result_shot = np.mean(shots, axis=0)
        elif self.combo.get() == 'Экс.Сглаживание':
            result_shot = shots[0]
            for shot in shots:
                result_shot = alpha * shot + (1 - alpha) * result_shot
        elif self.combo.get() == 'Медиана':
            result_shot = np.median(shots, axis=0)



        self.output_sockets['Снимок'].set_value(result_shot)


        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Пульсации', 'camera'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
