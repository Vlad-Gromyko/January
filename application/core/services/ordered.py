import os

import numpy as np
from PIL import Image

import configparser
import customtkinter as ctk
import tkinter.filedialog as fd

from application.core.events import Service, Event

from application.core.utility.mask import Mask
from application.widgets.maskwidget import MaskLabel

from tkinterdnd2 import TkinterDnD, DND_ALL

class Atlas(Service, ctk.CTkFrame):
    def __init__(self, master):
        Service.__init__(self)
        ctk.CTkFrame.__init__(self, master)
        self.name = 'Atlas'

        self.cages = []




        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=0, column=0, padx=5, pady=5)

        self.add_button = ctk.CTkButton(self.left_frame, text='\uFF0B', command=self.load_file)
        self.add_button.grid(row=0, column=0, padx=5, pady=5)
        self.add_button.cget("font").configure(size=100)

        self.clean_button = ctk.CTkButton(self.left_frame, text='Очистить', command=self.clean)
        self.clean_button.grid(row=1, column=0, padx=5, pady=5)

        self.scroll = ctk.CTkScrollableFrame(self, orientation='horizontal', width=960, height=150)
        self.scroll.grid(row=0, column=1, padx=5, pady=5)

        self.events_reactions['Add Atlas'] = lambda event: self.add_cage(event.get_value()['mask'],
                                                                         event.get_value()['text'])

        self.drop_target_register(DND_ALL)
        self.dnd_bind("<<Drop>>", self.to_drop)

    def to_drop(self, event):
        dropped_file = event.data.replace("{", "").replace("}", "")
        file = dropped_file.split('/')[-1]
        mode = file.split('.')[-1]
        if mode == 'npy':
            array = np.load(dropped_file)
            self.add_cage(Mask(array), file)
        if mode == 'bmp':
            array = np.asarray(Image.open(dropped_file))/255 * 2 * np.pi
            self.add_cage(Mask(array), file)
        self.drop_end()

    def drop_start(self):
        self.fg_color=self.cget('fg_color')

        self.configure(fg_color='#32CD32')

    def drop_end(self):
        self.configure(fg_color=self.fg_color)

    def load_file(self):
        files = fd.askopenfilenames(title="Загрузить голограмму", defaultextension=".bmp",
                                    filetypes=[('Numpy', '*.npy'), ('BitMap', '*.bmp*')],)

        if files != '':
            for file in files:
                if file.split('.')[-1] == 'npy':
                    array = np.load(file)
                    self.add_cage(Mask(array), text=file.split('/')[-1], trigger=False)

                if file.split('.')[-1] == 'bmp':
                    array = np.asarray(Image.open(file))/255 * 2 * np.pi
                    self.add_cage(Mask(array), text=file.split('/')[-1], trigger=False)

            self.event_bus.raise_event(Event(self.name + ' Changed', self.cages))



    def add_cage(self, mask: Mask, text, trigger=True):
        counter = len(self.cages)
        cage = Cage(self.scroll, mask, counter, text)

        self.cages.append(cage)
        cage.left_button.configure(command=lambda: self.left_move(cage.counter))
        cage.right_button.configure(command=lambda: self.right_move(cage.counter))
        cage.cross_button.configure(command=lambda: self.cross(cage.counter))
        self.grid_all()

        if trigger:
            self.event_bus.raise_event(Event(self.name + ' Changed', self.cages))
        self.add_menu(cage)

    def add_menu(self, cage):
        cage.mask.menu.add_command(label='Добавить в Сумматор',
                                   command=lambda: self.event_bus.raise_event(
                                       Event('Add Combiner',
                                             {'mask': cage.mask.get_mask(), 'text': cage.label.cget('text')})))

        cage.mask.menu.add_command(label='Добавить на Холст',
                                   command=lambda: self.event_bus.raise_event(
                                       Event('Add Node Holo',
                                             {'mask': cage.mask.get_mask(), 'text': cage.label.cget('text')})))

        cage.mask.menu.add_command(label='Отправить на SLM',
                                   command=lambda: self.event_bus.raise_event(
                                       Event('Set SLM Original',
                                             cage.mask.get_mask())))

    def forget_all(self):
        for cage in self.cages:
            cage.grid_forget()

    def grid_all(self):
        for i, cage in enumerate(self.cages):
            cage.grid(row=0, column=i, padx=5, pady=5)

    def left_move(self, counter):

        self.forget_all()
        if 0 < counter:
            cage_l = self.cages[counter - 1]
            cage_r = self.cages[counter]
            self.cages[counter] = cage_l
            self.cages[counter - 1] = cage_r

            cage_l.counter = counter
            cage_r.counter = counter - 1
        self.grid_all()

    def right_move(self, counter):
        self.forget_all()
        if counter < len(self.cages) - 1:
            cage_l = self.cages[counter]
            cage_r = self.cages[counter + 1]
            self.cages[counter + 1] = cage_l
            self.cages[counter] = cage_r

            cage_l.counter = counter + 1
            cage_r.counter = counter
        self.grid_all()

    def cross(self, counter):

        if len(self.cages) == 0:
            pass

        self.forget_all()

        for cage in self.cages:
            if cage.counter > counter:
                cage.counter -= 1
        cage_del = self.cages.pop(counter)
        self.grid_all()

        self.event_bus.raise_event(Event(self.name + ' Changed', self.cages))

    def clean(self):
        self.forget_all()
        self.cages = []

        self.event_bus.raise_event(Event(self.name + ' Changed', self.cages))

    def set_project(self, path):
        slm_folder = path + '/slm'
        config = configparser.ConfigParser()
        config.read(slm_folder + '/slm.ini')
        slm_name = config.sections()[0]

        slm_width = int(config[slm_name]['WIDTH'])
        slm_height = int(config[slm_name]['HEIGHT'])

        acc_folder = path + '/atlas'

        holos = os.listdir(acc_folder)

        for item in holos:
            array = np.load(item)
            self.add_cage(Mask(array), '', False)


class Cage(ctk.CTkFrame):
    def __init__(self, master, mask: Mask, counter, text=''):
        super().__init__(master)

        frame_buttons = ctk.CTkFrame(self, height=25)
        frame_buttons.grid(row=0, column=1, sticky='e')

        self.counter = counter

        self.label = ctk.CTkLabel(self, text=text)
        self.label.grid(row=0, column=0, sticky='w')

        self.left_button = ctk.CTkButton(frame_buttons, text='\u2BC7', width=20)
        self.left_button.grid(row=0, column=1, padx=2)

        self.right_button = ctk.CTkButton(frame_buttons, text='\u2BC8', width=20)
        self.right_button.grid(row=0, column=2, padx=2)

        self.cross_button = ctk.CTkButton(frame_buttons, text='\u2573', width=20, fg_color='#c94f4f')
        self.cross_button.grid(row=0, column=3, padx=2)

        self.mask = MaskLabel(self, mask, size_scale=1 / 10)
        self.mask.grid(row=1, columnspan=2)


class Combiner(Atlas):
    def __init__(self, master):
        super().__init__(master)

        self.name = 'Combiner'

        self.left_frame.grid(row=0, column=1, padx=5, pady=5)

        self.compose_label = MaskLabel(self, size_scale=1 / 8)
        self.compose_label.grid(row=0, column=0, padx=5, pady=5)

        self.compose_label.menu.add_command(label='Добавить в Атлас',
                                            command=lambda: self.event_bus.raise_event(
                                                Event('Add Atlas',
                                                      {'mask': self.compose_label.get_mask(),
                                                       'text': self.compose_label.label.cget('text')})))

        self.compose_label.menu.add_command(label='Добавить в Сумматор',
                                            command=lambda: self.event_bus.raise_event(
                                                Event('Add Combiner',
                                                      {'mask': self.compose_label.get_mask(),
                                                       'text': self.compose_label.label.cget('text')})))

        self.compose_label.menu.add_command(label='Добавить на Холст',
                                            command=lambda: self.event_bus.raise_event(
                                                Event('Add Node Holo',
                                                      {'mask': self.compose_label.get_mask(),
                                                       'text': self.compose_label.label.cget('text')})))

        self.compose_label.menu.add_command(label='Отправить на SLM',
                                            command=lambda: self.event_bus.raise_event(
                                                Event('Set SLM Original',
                                                      self.compose_label.get_mask())))

        self.scroll.configure(width=710)
        self.scroll.grid(row=0, column=2, padx=5, pady=5)

        self.events_reactions.pop('Add Atlas', None)
        self.events_reactions['Add Combiner'] = lambda event: self.add_cage(event.get_value()['mask'],
                                                                            event.get_value()['text'])

    def set_project(self, path):
        slm_folder = path + '/slm'
        config = configparser.ConfigParser()
        config.read(slm_folder + '/slm.ini')
        slm_name = config.sections()[0]

        slm_width = int(config[slm_name]['WIDTH'])
        slm_height = int(config[slm_name]['HEIGHT'])

        acc_folder = path + '/accumulator'

        holos = os.listdir(acc_folder)

        self.compose_label.set_mask(Mask(np.zeros((slm_height, slm_width))))

        for item in holos:
            array = np.load(item)
            self.add_cage(Mask(array),'', False)

    def add_cage(self, mask:Mask, text, trigger=True):
        super().add_cage(mask, text, trigger)
        self.sum_masks()

    def add_menu(self, cage):
        cage.mask.menu.add_command(label='Добавить в Атлас',
                                   command=lambda: self.event_bus.raise_event(
                                       Event('Add Atlas',
                                             {'mask': cage.mask.get_mask(), 'text': cage.label.cget('text')})))

        cage.mask.menu.add_command(label='Добавить на Холст',
                                   command=lambda: self.event_bus.raise_event(
                                       Event('Add Node Holo',
                                             {'mask': cage.mask.get_mask(), 'text': cage.label.cget('text')})))

        cage.mask.menu.add_command(label='Отправить на SLM',
                                   command=lambda: self.event_bus.raise_event(
                                       Event('Set SLM Original',
                                             cage.mask.get_mask())))

    def clean(self):
        super().clean()
        self.sum_masks()

    def cross(self, counter):
        super().cross(counter)
        self.sum_masks()

    def sum_masks(self):

        if len(self.cages) != 0:
            masks = [cage.mask.get_mask().get_array() for cage in self.cages]

            array = np.zeros_like(masks[0])

            for i in masks:
                array = array + i
            self.compose_label.set_mask(Mask(array))
