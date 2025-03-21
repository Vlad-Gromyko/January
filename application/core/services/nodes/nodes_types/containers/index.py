from application.core.events import Event
from application.core.services.nodes.node import INode


class Node(INode):
    def __init__(self, config, editor, canvas, x, y, text, theme, **kwargs):
        super().__init__(config, editor, canvas, x, y, text=text, theme=theme, **kwargs)

        self.add_enter_socket('Вектор', self.palette['ANY'])
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
