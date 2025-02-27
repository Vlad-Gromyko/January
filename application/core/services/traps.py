from abc import abstractmethod

import customtkinter as ctk

import numpy as np

import screeninfo
import cv2
from PIL import Image
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
import os
import configparser
import tksheet

from application.core.events import Service, Event
from application.core.utility.mask import Mask
from application.widgets.maskwidget import MaskLabel


class Traps(Service, ctk.CTkFrame):
    def __init__(self, master):
        Service.__init__(self)
        ctk.CTkFrame.__init__(self, master)
        self.name = 'Traps'

        ctk.CTkButton(self, text='Карта Ловушек \u287E', command=self.show_traps).grid(row=0, column=0, padx=5)

        f = ctk.CTkFrame(self)
        f.grid(row=0, column=1)

        ctk.CTkLabel(f, text='Масштаб').grid(row=0, column=0, padx=5)

        self.size = ctk.CTkEntry(f, width=50)
        self.size.grid(row=0, column=1, padx=5)
        self.size.insert(0, '1')

        ctk.CTkLabel(f, text='мкм').grid(row=0, column=2, padx=5)

        self.sheet = tksheet.Sheet(self, theme='dark blue', width=350,height=200,
                                   headers=['X', 'Y', 'Z', 'W'], default_column_width=65, show_x_scrollbar=False)

        self.sheet.grid(sticky='nsew', row=2, columnspan=2, pady=5)

        self.sheet.enable_bindings()

        self.sheet.disable_bindings('copy', 'rc_insert_column', 'paste', 'cut', 'Delete', 'Edit cell', 'Delete columns')

        self.sheet.set_options(insert_row_label='Добавить Ловушку')
        self.sheet.set_options(delete_rows_label='Удалить Ловушку')
        self.sheet.set_options(insert_rows_above_label='Добавить ловушку \u25B2')
        self.sheet.set_options(insert_rows_below_label='Добавить ловушку \u25BC')
        self.sheet.set_options(delete_rows_label='Удалить Ловушку')

        f1 = ctk.CTkFrame(self)

        f1.grid(row=3, column=0, columnspan=2)

        ctk.CTkLabel(f1, text='X:').grid(row=0, column=0, padx=5, pady=5)

        self.cx = ctk.CTkEntry(f1, width=50)
        self.cx.grid(row=0, column=1, padx=5, pady=5)
        self.cx.insert(0, '0')

        ctk.CTkLabel(f1, text='Y:').grid(row=0, column=2, padx=5, pady=5)

        self.cy = ctk.CTkEntry(f1, width=50)
        self.cy.grid(row=0, column=3, padx=5, pady=5)
        self.cy.insert(0, '0')

        ctk.CTkLabel(f1, text='Z:').grid(row=0, column=4, padx=5, pady=5)

        self.cz = ctk.CTkEntry(f1, width=50)
        self.cz.grid(row=0, column=5, padx=5, pady=5)
        self.cz.insert(0, '0')

        ctk.CTkLabel(f1, text='Угол \u2220:').grid(row=1, column=0, padx=5, pady=5)

        self.angle = ctk.CTkEntry(f1, width=50)
        self.angle.grid(row=1, column=1, padx=5, pady=5)
        self.angle.insert(0, '0')

        self.tabs = ctk.CTkTabview(self, height=100)
        self.tabs.grid(row=4, column=0, columnspan=2)
        self.arrays = ArrayGeometry(self, func=self.add_trap)
        self.arrays.grid()

        ctk.CTkButton(f1, text='Очистить', fg_color='#c94f4f', command=self.clear).grid(row=1, column=2, columnspan=4)

        self.fields['Traps'] = []

        self.sheet.bind('<<SheetModified>>', self.update_traps)

    def update_traps(self, event=None):
        self.fields['Traps'] = self.get_specs()

    def show_traps(self):
        x = []
        y = []
        w = []

        if self.sheet.get_total_rows() > 0:
            for i in range(self.sheet.get_total_rows()):
                spec = self.sheet[i].data
                if spec[0] != '' and spec[1] != '' and spec[2] != '' and spec[3] != '':
                    x.append(float(spec[0]))
                    y.append(float(spec[1]))
                    w.append(float(spec[3]))

            plt.style.use('dark_background')
            plt.scatter(x, y, c=w, alpha=0.7, cmap='hot', vmin=0, vmax=max(w))
            plt.colorbar(cmap='hot')
            plt.show()

    def add_trap(self, x=0, y=0, z=0, w=1):
        cx = float(self.cx.get())
        cy = float(self.cy.get())
        cz = float(self.cz.get())
        self.sheet.insert_row([(x + cx), y + cy, z + cz, w])
        self.update_traps()

    def clear(self):
        for i in range(self.sheet.get_total_rows()):
            self.sheet.del_row(0)
        self.update_traps()

    def delete(self):
        current_selection = self.sheet.get_currently_selected()
        if current_selection:
            box = current_selection.row
            self.sheet.delete_row(box)

    def get_specs(self):
        specs = []
        scale = float(self.size.get()) * 10 ** -6
        for i in range(self.sheet.get_total_rows()):
            spec = self.sheet[i].data
            if spec[0] != '' and spec[1] != '' and spec[2] != '' and spec[3] != '':
                specs.append((spec[0] * scale,
                              spec[1] * scale,
                              spec[2] * scale,
                              spec[3]))

        return specs


class TrapsGeometry(ctk.CTkFrame):
    def __init__(self, master: Traps, name, func):
        master.tabs.add(name)
        ctk.CTkFrame.__init__(self, master.tabs.tab(name), height=100)

        self.button = ctk.CTkButton(self, text='Добавить', command=self.calc_traps_geometry)
        self.button.grid(row=0, column=0, padx=5, pady=5)

        ctk.CTkLabel(self, text='W:').grid(row=0, column=1, padx=5, pady=5)

        self.w = ctk.CTkEntry(self, width=50)
        self.w.insert(0, '1')
        self.w.grid(row=0, column=2, padx=5, pady=5)
        self.func = func

    @abstractmethod
    def do_geometry(self):
        pass

    def calc_traps_geometry(self):
        traps = self.do_geometry()
        for trap in traps:
            self.func(trap[0], trap[1], trap[2], trap[3], )


class ArrayGeometry(TrapsGeometry):
    def __init__(self, master: Traps, func):
        super().__init__(master, 'Массив', func)

        f = ctk.CTkFrame(self, height=300)
        f.grid(row=1)

        ctk.CTkLabel(f, text='X', width=20).grid(row=0, column=1)
        ctk.CTkLabel(f, text='Y', width=20).grid(row=0, column=2)
        ctk.CTkLabel(f, text='Z', width=20).grid(row=0, column=3)
        ctk.CTkLabel(f, text='N', width=20).grid(row=1, column=0)
        ctk.CTkLabel(f, text='\u2195', width=20).grid(row=2, column=0)

        self.nx = ctk.CTkEntry(f, width=50)
        self.nx.insert(0, '5')
        self.nx.grid(row=1, column=1)

        self.ny = ctk.CTkEntry(f, width=50)
        self.ny.insert(0, '5')
        self.ny.grid(row=1, column=2)

        self.nz = ctk.CTkEntry(f, width=50)
        self.nz.insert(0, '1')
        self.nz.grid(row=1, column=3)

        self.dx = ctk.CTkEntry(f, width=50)
        self.dx.insert(0, '100')
        self.dx.grid(row=2, column=1)

        self.dy = ctk.CTkEntry(f, width=50)
        self.dy.insert(0, '100')
        self.dy.grid(row=2, column=2)

        self.dz = ctk.CTkEntry(f, width=50)
        self.dz.insert(0, '100')
        self.dz.grid(row=2, column=3)

    def do_geometry(self):
        x_n = int(self.nx.get())
        y_n = int(self.ny.get())
        z_n = int(self.nz.get())

        x_d = float(self.dx.get())
        y_d = float(self.dy.get())
        z_d = float(self.dz.get())

        x_c = 0
        y_c = 0
        z_c = 0

        x_line = [x_c - x_d * (x_n - 1) / 2 + x_d * i for i in range(x_n)]
        y_line = [y_c - y_d * (y_n - 1) / 2 + y_d * i for i in range(y_n)]
        z_line = [z_c - z_d * (z_n - 1) / 2 + z_d * i for i in range(z_n)]

        w = float(self.w.get())
        traps = []
        for z in z_line:
            for x in x_line:
                for y in y_line:
                    traps.append((x, y, z, w))

        return traps
