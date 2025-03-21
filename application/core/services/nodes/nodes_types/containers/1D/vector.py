from application.core.events import Event
from application.core.services.nodes.node import INode


class Node(INode):
    def __init__(self, config, editor, canvas, x, y, text, theme, **kwargs):
        super().__init__(config, editor, canvas, x, y, text=text, theme=theme, **kwargs)

        self.add_enter_socket('Длина', self.palette['NUM'])
        self.add_enter_socket('Элемент', self.palette['ANY'])

        self.add_output_socket('Вектор', self.palette['HOLOGRAM_LIST'])

    def execute(self):
        arguments = self.get_func_inputs()

        length = int(arguments['Длина'])
        element = arguments['Элемент']
        result = [element for i in range(length)]

        self.output_sockets['Вектор'].set_value(result)

    @staticmethod
    def create_info():
        return Node, 'Список Голограмм', 'container'
