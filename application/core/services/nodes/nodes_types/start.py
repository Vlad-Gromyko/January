from application.core.services.nodes.node import INode

class Node(INode):
    def __init__(self, special_id,config, editor, canvas, x, y,control, text, theme):
        super().__init__(special_id ,config,editor, canvas, x, y, control, text,theme)

        self.special_id = special_id

        self.label.configure(fg_color='#FFF')
        self.label.configure(text_color='#000')

        self.add_output_socket('', self.palette['SIGNAL'], self.width + 13, -self.height + 7)

        self.enter_height = 0
        self.output_height = 0

    def add_signal(self):
        pass

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
        return Node, 'Старт', 'program'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
