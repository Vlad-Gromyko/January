import customtkinter as ctk

from application.core.services.node import INode
from application.widgets.maskwidget import MaskLabel

from application.core.utility.mask import  Mask

class Node(INode):
    def __init__(self, editor, canvas, palette, x, y):
        super().__init__(editor, canvas, palette, x, y, text='Вихрь', color_text='#FFF', color_back='#0D5858')


        self.add_enter_socket('Заряд', self.palette['NUM'])
        self.add_output_socket('', self.palette['BOOL'])

        
        self.mask_label = MaskLabel(self.canvas)

    def execute(self):
        print(self.get_func_inputs())



