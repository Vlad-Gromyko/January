from application.core.services.nodes.node import INode

import time


class Node(INode):
    def __init__(self, config, editor, canvas, x, y, text, theme, **kwargs):
        super().__init__(config, editor, canvas, x, y, text, theme, **kwargs)

        self.add_enter_socket('', self.palette['SIGNAL'])
        self.add_output_socket('', self.palette['SIGNAL'])

        self.add_enter_socket('Сек.', self.palette['NUM'])


    def execute(self):
        arguments = self.get_func_inputs()

        time.sleep(arguments['Сек.'])

        self.output_sockets[''].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Пауза', 'program'