import customtkinter as ctk

from application.core.services.nodes.node import INode


class Node(INode):
    def __init__(self, config, editor, canvas, x, y, text, theme, **kwargs):
        super().__init__(config, editor, canvas, x, y, text=text, theme=theme, **kwargs)

        self.add_enter_socket('', self.palette['NUM'])
        self.add_output_socket('', self.palette['NUM'])

        self.widget_width = 120
        self.widget_height = 25
        frame_widgets = ctk.CTkFrame(self.canvas, width=self.widget_width, height=self.widget_height)
        self.frame_IDs['widgets'] = self.canvas.create_window(self.x, self.y, window=frame_widgets,
                                                              anchor=ctk.NW, width=self.widget_width,
                                                              height=self.widget_height)

        self.num_label = ctk.CTkLabel(frame_widgets, text='', anchor=ctk.NW)
        self.num_label.grid(padx=5, pady=5)

    def execute(self):
        arguments = self.get_func_inputs()

        self.num_label.configure(text=arguments[''])
        self.num_label.update_idletasks()
        self.output_sockets[''].set_value(arguments[''])

    @staticmethod
    def create_info():
        return Node, 'Повторитель', 'math'
