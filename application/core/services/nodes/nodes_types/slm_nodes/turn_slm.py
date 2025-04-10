from application.core.events import Event
from application.core.services.nodes.node import INode


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('', self.palette['SIGNAL'])
        self.add_output_socket('', self.palette['SIGNAL'])

    def execute(self):
        arguments = self.get_func_inputs()

        self.event_bus.raise_event(Event('Toggle SLM'))

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Вкл/Выкл SLM', 'slm'

    def prepare_save_spec(self):
        return __file__, self.x, self.y, {}, self.special_id, self.with_signals