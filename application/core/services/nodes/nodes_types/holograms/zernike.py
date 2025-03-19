from application.core.events import Event
from application.core.services.nodes.node import INode


class Node(INode):
    def __init__(self, config, editor, canvas, palette, x, y, text, theme, **kwargs):
        super().__init__(config, editor, canvas, palette, x, y, text=text, theme=theme, **kwargs)

        self.add_enter_socket('', self.palette['SIGNAL'])
        self.add_enter_socket('Амплитуда', self.palette['NUM'])
        self.add_enter_socket('Номер', self.palette['NUM'])

        self.add_output_socket('', self.palette['SIGNAL'])
        self.add_output_socket('Голограмма', self.palette['HOLOGRAM'])



    def execute(self):
        arguments = self.get_func_inputs()

        self.event_bus.raise_event(Event('Calculate Zernike One', {'number': arguments['Номер'],
                                                                   'amplitude':arguments['Амплитуда']}))
        holo = self.event_bus.get_field('Last Zernike Mask')

        self.output_sockets['Голограмма'].set_value(holo)
        self.output_sockets[''].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Цернике', 'hologram'