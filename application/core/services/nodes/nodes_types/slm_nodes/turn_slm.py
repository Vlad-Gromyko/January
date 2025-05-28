import customtkinter as ctk

from application.core.events import Event
from application.core.services.nodes.node import INode


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.load_data = kwargs
        self.strong_control = True

        self.widget_width = 30
        self.widget_height = 30
        frame_widgets = ctk.CTkFrame(self.canvas, width=self.widget_width, height=self.widget_height)
        self.frame_IDs['widgets'] = self.canvas.create_window(self.x, self.y, window=frame_widgets,
                                                              anchor=ctk.NW, width=self.widget_width,
                                                              height=self.widget_height)

        self.label.configure(fg_color='#FFF')
        self.label.configure(text_color='#000')

        self.button = ctk.CTkButton(frame_widgets, text='', command=self.execute, text_color='#000', fg_color='#FFF',
                                    width=20, height=20)
        self.button.grid(padx=5, pady=5)

    def execute(self):
        arguments = self.get_func_inputs()

        self.event_bus.raise_event(Event('Toggle SLM'))

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Вкл/Выкл SLM', 'slm'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals