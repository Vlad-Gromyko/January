from application.core.events import Event
from application.core.services.nodes.node import INode
import customtkinter as ctk
import time


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id



        self.add_output_socket('', self.palette['SIGNAL'])

        self.load_data = kwargs
        self.strong_control = True

        self.widget_width = 50
        self.widget_height = 40
        frame_widgets = ctk.CTkFrame(self.canvas, width=self.widget_width, height=self.widget_height)
        self.frame_IDs['widgets'] = self.canvas.create_window(self.x, self.y, window=frame_widgets,
                                                              anchor=ctk.NW, width=self.widget_width,
                                                              height=self.widget_height)

        self.execution_status = True

        self.button = ctk.CTkButton(frame_widgets, text='', command=self.on_click, fg_color='green', width=20, height=20)
        self.button.grid(row=0, column=0, padx=10, pady=10, sticky='nsew', rowspan=1, columnspan=1)


    def on_click(self):
        if self.execution_status:
            self.execution_status = False
            self.button.configure( fg_color='red')
            self.execute()
        else:
            self.execution_status = True
            self.button.configure( fg_color='green')



    def execute(self):
        arguments = self.get_func_inputs()

        if self.execution_status:
            self.output_sockets[''].set_value(True)


        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Pipe', 'program'

    @staticmethod
    def possible_to_create():
        return True

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
