from application.core.events import Event
from application.core.services.nodes.node import INode


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id


        self.add_enter_socket('Амплитуда', self.palette['NUM'])
        self.add_enter_socket('Номер', self.palette['NUM'])


        self.add_output_socket('Голограмма', self.palette['HOLOGRAM'])



    def execute(self):
        arguments = self.get_func_inputs()

        self.event_bus.raise_event(Event('Calculate Zernike One', {'number': arguments['Номер'],
                                                                   'amplitude':arguments['Амплитуда']}))
        holo = self.event_bus.get_field('Last Zernike Mask')

        self.output_sockets['Голограмма'].set_value(holo)
        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)



    @staticmethod
    def create_info():
        return Node, 'Цернике', 'hologram'

    def prepare_save_spec(self):
        return __file__, self.x, self.y, {}, self.special_id, self.with_signals