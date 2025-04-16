from application.core.services.nodes.node import INode

class Node(INode):
    def __init__(self, special_id,config, editor, canvas, x, y,control, text, theme, **kwargs):
        super().__init__(special_id ,config,editor, canvas, x, y, control, text,theme, **kwargs)

        self.special_id = special_id

        self.label.configure(fg_color='#FFF')
        self.label.configure(text_color='#000')

        self.add_output_socket('', self.palette['SIGNAL'], self.width + 13, -self.height + 7)

        self.enter_height = 0
        self.output_height = 0

    def add_signal(self):
        pass

    def add_menu(self):
        self.menu.add_command(label='Информация    \u003F', command=self.show_info)
        self.menu.add_command(label='Дублировать    +', command=self.add_clone)
        self.menu.add_command(label='Показать Код', command=self.show_code)
        self.menu.add_separator()
        self.menu.add_command(label='Удалить        \u2573', command=self.delete_node)

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
