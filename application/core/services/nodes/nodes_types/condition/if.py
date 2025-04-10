from application.core.events import Event
from application.core.services.nodes.node import INode
import customtkinter as ctk
import time


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Условие', self.palette['BOOL'])

        self.add_enter_socket('True', self.palette['SIGNAL'])
        self.add_output_socket('False', self.palette['SIGNAL'])




    def execute(self):
        arguments = self.get_func_inputs()


        if arguments['Условие']:
            self.output_sockets['True'].set_value(True)
        else:
            self.output_sockets['False'].set_value(True)

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'If/Else', 'program'

    @staticmethod
    def possible_to_create():
        return True

    def prepare_save_spec(self):
        return __file__, self.x, self.y, {}, self.special_id, self.with_signals
