import customtkinter as ctk
import tkinter

from scipy.constants import value

from application.core.services.nodes.node import INode


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_output_socket('', self.palette['NUM'])
        self.load_data = kwargs
        entry = 1
        if 'value' in kwargs.keys():
            entry = kwargs['value']

        sv = tkinter.StringVar()
        self.entry = ctk.CTkEntry(self.canvas, width=50, textvariable=sv)
        self.entry.insert(0, str(entry))

        self.frame_IDs['entry'] = self.canvas.create_window(self.x, self.y + self.height, window=self.entry,
                                                            anchor=ctk.NW)

        sv.trace("w", lambda *args: self.execute())
        self.execute()

    def execute(self):
        entry = (self.entry.get())
        try:
            entry = float(entry)
            self.output_sockets[''].set_value(float(entry))
            if 'go' in self.output_sockets.keys():
                self.output_sockets['go'].set_value(True)
        except ValueError:
            pass

    @staticmethod
    def create_info():
        return Node, 'Число', 'math'

    def prepare_save_spec(self):
        data = {'value': self.entry.get()}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
