from application.core.events import Event
from application.core.services.nodes.node import INode


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Число Строк', self.palette['NUM'])
        self.add_enter_socket('Число Столбцов', self.palette['NUM'])
        self.add_enter_socket('Элемент', self.palette['ANY'])

        self.add_output_socket('Вектор', self.palette['vector2d'])

    def execute(self):
        arguments = self.get_func_inputs()

        rows = int(arguments['Число Строк'])
        columns = int(arguments['Число Столбцов'])
        element = arguments['Элемент']

        result = [[element for i in range(columns)] for j in range(rows)]

        self.output_sockets['Вектор'].set_value(result)

    @staticmethod
    def create_info():
        return Node, 'Вектор 2D', 'container'

    def prepare_save_spec(self):
        return __file__, self.x, self.y, {}, self.special_id