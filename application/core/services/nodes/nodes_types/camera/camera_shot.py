from application.core.events import Event
from application.core.services.nodes.node import INode


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Фон', self.palette['SIGNAL'])
        self.add_enter_socket('Снимок', self.palette['SIGNAL'])

        self.add_output_socket('', self.palette['SIGNAL'])
        self.add_output_socket('Снимок', self.palette['CAMERA_SHOT'])
        self.add_output_socket('Фон', self.palette['CAMERA_SHOT'])
        self.add_output_socket('Снимок - Фон', self.palette['CAMERA_SHOT'])

        self.load_data = kwargs

    def execute(self):
        arguments = self.get_func_inputs()
        if arguments['Снимок'] is not None:
            self.event_bus.raise_event(Event('Take Shot'))

        elif arguments['Фон'] is not None:
            self.event_bus.raise_event(Event('Take Back'))

        back = self.event_bus.get_field('Back')
        shot = self.event_bus.get_field('Shot')
        shot_back = self.event_bus.get_field('Shot - Back')

        self.output_sockets['Фон'].set_value(back)
        self.output_sockets['Снимок'].set_value(shot)
        self.output_sockets['Снимок - Фон'].set_value(shot_back)

        self.output_sockets[''].set_value(True)

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Камера', 'camera'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals

    def saves_dict(self):
        enters = dict()
        for item in self.enter_sockets.values():
            enters[item.name + '_enter'] = item.get_value()

        outputs = dict()
        for item in self.output_sockets.values():
            outputs[item.name + '_output'] = item.get_value()

        return {**enters, **outputs}