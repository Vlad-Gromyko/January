from application.core.events import Event
from application.core.services.nodes.node import INode


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, text, theme)

        self.special_id = special_id

        self.add_enter_socket('', self.palette['SIGNAL'])
        self.add_enter_socket('Голограмма', self.palette['HOLOGRAM'])

        self.add_output_socket('', self.palette['SIGNAL'])

    def execute(self):
        arguments = self.get_func_inputs()

        self.event_bus.raise_event(Event('Set SLM Original', arguments['Голограмма']))

        self.output_sockets[''].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'SLM', 'slm'
    def prepare_save_spec(self):
        return __file__, self.x, self.y, {}