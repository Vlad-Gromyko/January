from application.core.events import Event
from application.core.services.nodes.node import INode


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, text, theme)

        self.special_id = special_id

        self.add_enter_socket('От', self.palette['NUM'])
        self.add_enter_socket('Шаг', self.palette['NUM'])
        self.add_enter_socket('До', self.palette['NUM'])

        self.add_output_socket('List', self.palette['NUM_LIST'])

    def execute(self):
        arguments = self.get_func_inputs()

        start = int(arguments['От'])
        step = int(arguments['Шаг'])
        end = int(arguments['До'])

        self.output_sockets['List'].set_value(list(range(start, end, step)))

    @staticmethod
    def create_info():
        return Node, 'Range', 'container'
    def prepare_save_spec(self):
        return __file__, self.x, self.y, {}