from application.core.services.nodes.node import INode


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Вектор', self.palette['vector1d'])


        self.add_output_socket('Тело Цикла', self.palette['SIGNAL'])
        self.add_output_socket('Индекс', self.palette['NUM'])
        self.add_output_socket('Объект', self.palette['ANY'])


    def execute(self):
        arguments = self.get_func_inputs()


        for counter, item in enumerate(arguments['Контейнер']):
            self.output_sockets['Тело Цикла'].set_value(None)

            self.output_sockets['Индекс'].set_value(counter)

            self.output_sockets['Объект'].set_value(item)

            self.output_sockets['Тело Цикла'].set_value(True)

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'For Item', 'program'

    def prepare_save_spec(self):
        return __file__, self.x, self.y, {}, self.special_id, self.with_signals