import numpy as np

from application.core.events import Event
from application.core.services.nodes.node import INode
import customtkinter as ctk

from application.core.utility.mask import Mask
import time


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id
        self.load_data = kwargs

        if 'value_type' in kwargs.keys():
            self.value_type = kwargs['value_type']
        else:
            self.value_type = 'num'

        self.add_output_socket('', self.palette[self.value_type], self.width + 13)

        self.add_enter_socket('', self.palette[self.value_type], - 18)


        self.output_sockets[''].set_color(self.palette[self.value_type], delete_wires=False)
        self.enter_sockets[''].set_color(self.palette[self.value_type], delete_wires=False)

        self.enter_height = 0
        self.output_height = 0

        self.widget_width = 200
        self.widget_height = 0

        frame_widgets = ctk.CTkFrame(self.canvas, width=self.widget_width, height=self.widget_height)
        self.frame_IDs['widgets'] = self.canvas.create_window(self.x, self.y, window=frame_widgets,
                                                              anchor=ctk.NW, width=self.widget_width,
                                                              height=self.widget_height)

        self.vector_label = ctk.CTkLabel(frame_widgets, width=200)
        self.vector_label.pack()

        self.combo = ctk.CTkComboBox(frame_widgets, values=list(self.palette.keys()), command=self.combo_changed)
        self.combo.set(self.value_type)

        self.combo.pack()

        if 'name' in kwargs.keys():
            self.vector_label.configure(text=kwargs['name'])
            self.vector_name = kwargs['name']


        self.events_reactions['Value Updated'] = lambda event: self.vector_updated(event)
        self.events_reactions['Value Type Changed'] = lambda event: self.change_type(event)

        self.ready_to_execute = True

        self.null_types = None

        self.output_sockets[''].set_value(None)

    def combo_changed(self, word):

        self.event_bus.raise_event(
            Event('Value Type Changed', {'name': self.vector_name, 'type': word, 'tab': self.editor}))

        width = self.event_bus.get_field('slm width')
        height = self.event_bus.get_field('slm height')

        null_types = {
                      'bool': False,
                      'num': 0,
                      'str': '',
                      'hologram': Mask(np.zeros((height, width))),
                      'camera_shot': np.zeros((200, 200)),
                      'vector1d': [],
                      'vector2d': [[]],
                      'any': None}

        self.event_bus.raise_event(
            Event('Value Updated', {'name': self.vector_name, 'value': null_types[word], 'tab': self.editor}))

    def change_type(self, event):
        name = event.get_value()['name']
        tab = event.get_value()['tab']

        if name == self.vector_name and self.editor == tab:
            self.output_sockets[''].set_color(self.palette[event.get_value()['type']])
            self.enter_sockets[''].set_color(self.palette[event.get_value()['type']])
            self.combo.set(event.get_value()['type'])
            self.value_type = event.get_value()['type']

    def add_clone(self):
        self.editor.add_node(self.__class__, name=self.vector_name, value_type=self.value_type)

    def vector_updated(self, event):
        name = event.get_value()['name']
        tab = event.get_value()['tab']

        if name == self.vector_name and self.editor == tab and self.ready_to_execute:
            self.output_sockets[''].set_value(event.get_value()['value'])

    def execute(self):
        arguments = self.get_func_inputs()

        self.ready_to_execute = False

        self.event_bus.raise_event(
            Event('Value Updated', {'name': self.vector_name, 'value': arguments[''], 'tab': self.editor}))
        print(arguments[''])

        self.ready_to_execute = True

        self.output_sockets[''].set_value(arguments[''])

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Вектор', 'Container'

    @staticmethod
    def possible_to_create():
        return False

    def prepare_save_spec(self):
        data = {'name': self.vector_name, 'value_type': self.value_type}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
