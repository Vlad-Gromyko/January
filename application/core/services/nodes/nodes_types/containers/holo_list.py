from application.core.events import Event
from application.core.services.nodes.node import INode


class Node(INode):
    def __init__(self, config, editor, canvas, palette, x, y, text, theme, **kwargs):
        super().__init__(config, editor, canvas, palette, x, y, text=text, theme=theme, **kwargs)

        self.add_enter_socket('Добавить', self.palette['SIGNAL'])
        self.add_enter_socket('Голограмма', self.palette['HOLOGRAM'])

        self.add_enter_socket('Отдать', self.palette['SIGNAL'])
        self.add_enter_socket('Очистить', self.palette['SIGNAL'])

        self.add_output_socket('Список', self.palette['HOLO_LIST'])

        self.holos = list()

    def execute(self):
        arguments = self.get_func_inputs()


        item = arguments['Голограмма']

        

        self.output_sockets['List'].set_value()

    @staticmethod
    def create_info():
        return Node, 'Список Голограмм', 'container'
