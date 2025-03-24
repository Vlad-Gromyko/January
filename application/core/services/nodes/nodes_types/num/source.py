import customtkinter as ctk
import tkinter

from application.core.services.nodes.node import INode


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, text, theme)

        self.special_id = special_id

        self.add_output_socket('', self.palette['NUM'])

        value = 1
        sv = tkinter.StringVar()
        self.entry = ctk.CTkEntry(self.canvas, width=50, textvariable=sv)
        self.entry.insert(0, str(value))

        self.frame_IDs['entry'] = self.canvas.create_window(self.x, self.y + self.height, window=self.entry,
                                                            anchor=ctk.NW)

        sv.trace("w", lambda *args: self.execute())
        self.execute()

    def execute(self):
        value = (self.entry.get())
        try:
            value = float(value)
            self.output_sockets[''].set_value(float(value))
        except ValueError:
            pass

    @staticmethod
    def create_info():
        return Node, 'Число', 'math'

    def prepare_save_spec(self):
        return __file__, self.x, self.y, {}, self.special_id