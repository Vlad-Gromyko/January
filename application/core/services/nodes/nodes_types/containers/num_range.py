from application.core.events import Event
from application.core.services.nodes.node import INode


class Node(INode):
    def __init__(self, config, editor, canvas, palette, x, y, text, theme, **kwargs):
        super().__init__(config, editor, canvas, palette, x, y, text=text, theme=theme, **kwargs)

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
        return Node, 'Range', 'math'
