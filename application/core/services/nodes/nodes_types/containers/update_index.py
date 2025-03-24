from application.core.events import Event
from application.core.services.nodes.node import INode


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Вектор', self.palette['vector1d'])
        self.add_enter_socket('Индекс', self.palette['NUM'])
        self.add_enter_socket('"Элемент"', self.palette['ANY'])


        self.add_output_socket('Вектор', self.palette['vector1d'])

    def execute(self):
        arguments = self.get_func_inputs()

        index = int(arguments['Индекс'])
        container = arguments['Вектор']
        element = arguments['Элемент']
        container[index] = element

        self.output_sockets['Вектор'].set_value(container)

    @staticmethod
    def create_info():
        return Node, 'Обновить Элемент', 'container'

    def prepare_save_spec(self):
        return __file__, self.x, self.y, {}, self.special_id