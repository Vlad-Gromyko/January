from application.core.services.nodes.node import INode

class Start(INode):
    def __init__(self,config, editor, canvas, palette, x, y, text, theme):
        super().__init__(config,editor, canvas, palette, x, y, text,theme)

        self.label.configure(fg_color='#FFF')
        self.label.configure(text_color='#000')

        self.add_output_socket('', self.palette['SIGNAL'], self.width + 13, -self.height + 7)
        self.add_enter_socket('', self.palette['SIGNAL'], self.width + 13, -self.height + 7)

        self.enter_height = 0
        self.output_height = 0

    def add_menu(self):
        self.menu.add_command(label='Информация', command=self.show_info)

    def execute(self):
        self.output_sockets[''].set_value(True)
        self.output_sockets[''].set_value(None)

    def choose(self):
        self.chosen_one = True
        self.label.configure(fg_color='#4682B4')

    def no_choose(self):
        self.chosen_one = False
        self.label.configure(fg_color='#FFF')

    @staticmethod
    def create_info():
        return Start, 'Старт', 'program'
