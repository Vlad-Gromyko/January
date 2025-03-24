from application.core.events import Event
from application.core.services.nodes.node import INode


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Вектор', self.palette['vector1d'])
        self.add_enter_socket('Индекс', self.palette['NUM'])


        self.add_output_socket('Объект', self.palette['ANY'])

    def execute(self):
        arguments = self.get_func_inputs()

        index = int(arguments['Индекс'])
        container = arguments['Вектор']

        self.output_sockets['Объект'].set_value(container[index])

    @staticmethod
    def create_info():
        return Node, 'Элемент Вектора', 'container'

    def prepare_save_spec(self):
        return __file__, self.x, self.y, {}, self.special_id