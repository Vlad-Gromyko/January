from application.core.services.nodes.node import INode


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id


        self.add_enter_socket('От', self.palette['NUM'])
        self.add_enter_socket('Шаг', self.palette['NUM'])
        self.add_enter_socket('До', self.palette['NUM'])

        self.add_output_socket('Тело Цикла', self.palette['SIGNAL'])
        self.add_output_socket('Индекс', self.palette['NUM'])
        self.load_data = kwargs
        self.strong_control = True

    def execute(self):
        arguments = self.get_func_inputs()

        for i in range(int(arguments['От']), int(arguments['До']),
                       int(arguments['Шаг'])):
            self.output_sockets['Тело Цикла'].set_value(None)

            self.output_sockets['Индекс'].set_value(i)

            self.output_sockets['Тело Цикла'].set_value(True)

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'For Range', 'program'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals