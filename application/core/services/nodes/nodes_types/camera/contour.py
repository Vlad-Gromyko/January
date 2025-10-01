import numpy as np
import customtkinter as ctk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
import matplotlib.pyplot as plt
from application.core.events import Event
from application.core.services.nodes.node import INode
import cv2
import time
class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Снимок', self.palette['CAMERA_SHOT'])

        self.add_output_socket('Компактность', self.palette['NUM'])


        self.load_data = kwargs

        self.widget_width = 500
        self.widget_height = 500
        frame_widgets = ctk.CTkFrame(self.canvas, width=self.widget_width, height=self.widget_height)
        self.frame_IDs['widgets'] = self.canvas.create_window(self.x, self.y, window=frame_widgets,
                                                              anchor=ctk.NW, width=self.widget_width,
                                                              height=self.widget_height)

        self.fig = Figure(figsize=(7, 7), dpi=100)

        self.ax = self.fig.add_subplot(111)

        self.plot_canvas = FigureCanvasTkAgg(self.fig,
                                             master=frame_widgets)
        self.plot_canvas.draw()

        self.plot_canvas.get_tk_widget().pack()

    def execute(self):
        arguments = self.get_func_inputs()

        image = arguments['Снимок']

        uint_img = np.array(image*255).astype('uint8')



        _, binary = cv2.threshold(uint_img, 0, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(uint_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        all_points = np.vstack([contour for contour in contours])
        hull = cv2.convexHull(all_points)

        area = cv2.contourArea(hull)
        perimeter = cv2.arcLength(hull, True)

        compactness = (perimeter ** 2) / area


        self.output_sockets['Компактность'].set_value(compactness)

        image_with_contours = uint_img.copy()
        cv2.drawContours(image_with_contours, contours, -1, (255, 0, 0), 2)
        cv2.drawContours(image_with_contours, [hull], -1, (0, 255, 0), 3)



        self.ax.cla()
        plt.tight_layout()

        self.ax.imshow(image_with_contours, cmap='hot')

        self.plot_canvas.draw()
        self.plot_canvas.flush_events()


        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Контур', 'camera'

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