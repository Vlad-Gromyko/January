import customtkinter as ctk

import numpy as np

import screeninfo
import cv2

import os
import configparser

from application.core.events import Service, Event
from application.core.utility.mask import Mask
from application.widgets.maskwidget import MaskLabel


class SLM(Service, ctk.CTkToplevel):
    def __init__(self, master):
        Service.__init__(self)
        ctk.CTkToplevel.__init__(self, master)
        self.name = 'SLM'
        self.title(self.name)

        notebook = ctk.CTkTabview(self, anchor='w', width=350)
        notebook.grid(padx=5, pady=5, sticky='nsew')

        notebook.add('SLM')
        notebook.add('Голограмма')
        notebook.add('Сдвиг')
        notebook.add('Калибровка')
        notebook.add('Аберрации')

        t1 = notebook.tab('SLM')
        t2 = notebook.tab('Голограмма')
        t3 = notebook.tab('Сдвиг')
        t4 = notebook.tab('Калибровка')
        t5 = notebook.tab('Аберрации')

        self.masks = {}

        self.masks['total'] = MaskLabel(t1, size_scale=1 / 8)
        self.masks['total'].grid(row=0, column=0, padx=5, pady=5)

        self.masks['holo'] = MaskLabel(t2, size_scale=1 / 8)
        self.masks['holo'].grid(row=0, column=0, padx=5, pady=5)

        self.masks['shift'] = MaskLabel(t3, size_scale=1 / 8)
        self.masks['shift'].grid(row=0, column=0, padx=5, pady=5)

        self.masks['calibrate'] = MaskLabel(t4, size_scale=1 / 8)
        self.masks['calibrate'].grid(row=0, column=0, padx=5, pady=5)

        self.masks['aberration'] = MaskLabel(t5, size_scale=1 / 8)
        self.masks['aberration'].grid(row=0, column=0, padx=5, pady=5)

        self.checks = []
        self.check_vars = []

        self.check_vars.append(ctk.StringVar(value="on"))
        self.checks.append(
            ctk.CTkCheckBox(t1, text="Транслировать", command=self.show, variable=self.check_vars[0], onvalue="on",
                            offvalue="off"))
        self.checks[0].deselect()

        self.checks[0].grid(row=1, column=0, padx=5, pady=5, sticky='ew')

        self.check_vars.append(ctk.StringVar(value="on"))
        self.checks.append(ctk.CTkCheckBox(t2, text="Добавить",
                                           variable=self.check_vars[1], onvalue="on", offvalue="off"))
        self.checks[1].grid(row=1, column=0, padx=5, pady=5, sticky='ew')

        self.check_vars.append(ctk.StringVar(value="on"))
        self.checks.append(ctk.CTkCheckBox(t3, text="Добавить",
                                           variable=self.check_vars[2], onvalue="on", offvalue="off"))
        self.checks[2].grid(row=1, column=0, padx=5, pady=5, sticky='ew')

        self.check_vars.append(ctk.StringVar(value="on"))
        self.checks.append(ctk.CTkCheckBox(t4, text="Добавить",
                                           variable=self.check_vars[3], onvalue="on", offvalue="off"))
        self.checks[3].grid(row=1, column=0, padx=5, pady=5, sticky='ew')

        self.check_vars.append(ctk.StringVar(value="on"))
        self.checks.append(ctk.CTkCheckBox(t5, text="Добавить",
                                           variable=self.check_vars[4], onvalue="on", offvalue="off"))
        self.checks[4].grid(row=1, column=0, padx=5, pady=5, sticky='ew')

        self.events_reactions['Set SLM Original'] = lambda event: self.set_slm(event.get_value())


        self.slm_width = 0
        self.slm_height = 0
        self.slm_gray = 0
        self.monitor = 1
        self.pixel_in_um = 1

        self.events_reactions['Toggle SLM'] = lambda event: self.checks[0].toggle()

        self.withdraw()

        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.events_reactions['Show/Hide Service SLM'] = lambda event: self.deiconify()

        self.visible = False

    def show_and_hide(self):
        if self.visible:
            self.withdraw()
        else:
            self.deiconify()
        self.visible = not self.visible

    def on_closing(self):
        self.visible = False
        self.withdraw()


    def set_project(self, path):
        slm_folder = path
        config = configparser.ConfigParser()
        config.read(path + '/field.ini')
        slm_name = config.sections()[0]

        self.slm_width = int(config['SLM']['WIDTH'])
        self.slm_height = int(config['SLM']['HEIGHT'])
        self.slm_gray = int(config['SLM']['GRAY'])
        self.monitor = int(config['SLM']['MONITOR'])
        self.pixel_in_um = int(config['SLM']['PIXEL_IN_UM'])

        for item in ['total', 'holo', 'shift', 'calibrate', 'aberration']:
            if os.path.exists(slm_folder + '/' + item):
                array = np.load(slm_folder + '/' + item)
            else:
                array = np.zeros((self.slm_height, self.slm_width))
            mask = Mask(array)
            self.masks[item].set_mask(mask)

    def set_slm(self, mask: Mask):
        self.masks['holo'].set_mask(mask)
        self.redraw_slm()
        if cv2.getWindowProperty('SLM', cv2.WND_PROP_VISIBLE):
            cv2.imshow('SLM', self.masks['total'].get_pixels())

        cv2.waitKey(1)

    def redraw_slm(self):
        arrays = []
        for item in [ self.masks['holo'], self.masks['shift'], self.masks['calibrate'],
                     self.masks['aberration']]:
            if item.mask is not None:
                arrays.append(item.get_mask().get_array())

        if len(arrays) != 0:
            array = np.sum(arrays, axis=0)
            self.masks['total'].set_mask(Mask(array))
            self.event_bus.raise_event(Event('SLM Changed'))

    def show(self):
        if self.masks['total'].get_mask() is not None:
            if self.checks[0].get() == 'off':
                if cv2.getWindowProperty('SLM', cv2.WND_PROP_VISIBLE):
                    cv2.destroyWindow('SLM')
            elif self.checks[0].get() == 'on':
                screen_id = self.monitor
                screen = screeninfo.get_monitors()[screen_id]

                cv2.namedWindow('SLM', cv2.WND_PROP_FULLSCREEN)
                cv2.moveWindow('SLM', screen.x - 1, screen.y - 1)
                cv2.setWindowProperty('SLM', cv2.WND_PROP_FULLSCREEN,
                                      cv2.WINDOW_FULLSCREEN)
                image = self.masks['total'].get_pixels()
                cv2.imshow('SLM', image)
        else:
            self.checks[0].deselect()

    def start_service(self, event: Event):
        pass
