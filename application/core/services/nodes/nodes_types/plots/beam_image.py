import customtkinter as ctk
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

from application.core.services.nodes.node import INode
from application.core.utility.mask import Mask


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('', self.palette['CAMERA_SHOT'])

        self.load_data = kwargs
        self.widget_width = 1000
        self.widget_height = 800
        frame_widgets = ctk.CTkFrame(self.canvas, width=self.widget_width, height=self.widget_height)
        self.frame_IDs['widgets'] = self.canvas.create_window(self.x, self.y, window=frame_widgets,
                                                              anchor=ctk.NW, width=self.widget_width,
                                                              height=self.widget_height)

        self.fig = plt.figure(figsize=(12, 10))
        self.gs = GridSpec(4, 4, figure=self.fig)

        self.ax_main = self.fig.add_subplot(self.gs[1:3, 1:3])



        self.plot_canvas = FigureCanvasTkAgg(self.fig,
                                             master=frame_widgets)
        self.plot_canvas.draw()

        self.plot_canvas.get_tk_widget().pack()

    def execute(self):
        arguments = self.get_func_inputs()

        image = arguments['']
        image = np.flip(image, axis=0)

        y_coords, x_coords = np.indices(image.shape)
        total_intensity = np.sum(image)
        centroid_x = np.sum(x_coords * image) / total_intensity
        centroid_y = np.sum(y_coords * image) / total_intensity

        # Вычисляем суммы по осям
        sum_x = np.sum(image, axis=0)  # сумма по строкам (по оси y)
        sum_y = np.sum(image, axis=1)  # сумма по столбцам (по оси x)

        self.ax_main.cla()

        im = self.ax_main.imshow(image, cmap='viridis', aspect='auto', origin='lower')

        self.ax_main.axhline(y=centroid_y, color='red', linestyle='--', linewidth=2,
                        label=f'Центроид Y: {centroid_y:.2f}')
        self.ax_main.axvline(x=centroid_x, color='red', linestyle='--', linewidth=2,
                        label=f'Центроид X: {centroid_x:.2f}')

        # Отмечаем точку центроида
        self.ax_main.plot(centroid_x, centroid_y, 'ro', markersize=8,
                     label='Центроид')

        self.ax_main.set_title('Пучок')
        self.ax_main.legend()

        ax_sum_x = self.fig.add_subplot(self.gs[0, 1:3])
        ax_sum_x.plot(sum_x, 'b-', linewidth=2)
        ax_sum_x.axvline(x=centroid_x, color='red', linestyle='--', linewidth=2)
        ax_sum_x.set_ylabel('Сумма по Y')
        ax_sum_x.set_title('Профиль по горизонтали')
        ax_sum_x.grid(True, alpha=0.3)

        # График суммы по Y (справа)
        ax_sum_y = self.fig.add_subplot(self.gs[1:3, 3])
        ax_sum_y.plot(sum_y, np.arange(len(sum_y)), 'b-', linewidth=2)
        ax_sum_y.axhline(y=centroid_y, color='red', linestyle='--', linewidth=2)
        ax_sum_y.set_xlabel('Сумма по X')
        ax_sum_y.set_title('Профиль по вертикали')
        ax_sum_y.grid(True, alpha=0.3)

        # Профили интенсивности относительно центроида (снизу)
        ax_profile_x = self.fig.add_subplot(self.gs[3, 1:3])
        x_profile = image[int(centroid_y), :]
        ax_profile_x.plot(x_profile, 'g-', linewidth=2, label='Профиль по X')
        ax_profile_x.axvline(x=centroid_x, color='red', linestyle='--', linewidth=2)
        ax_profile_x.set_xlabel('Координата X')
        ax_profile_x.set_ylabel('Интенсивность')
        ax_profile_x.set_title(f'Профиль интенсивности при Y={int(centroid_y)}')
        ax_profile_x.grid(True, alpha=0.3)
        ax_profile_x.legend()

        ax_profile_y = self.fig.add_subplot(self.gs[1:3, 0])
        y_profile = image[:, int(centroid_x)]
        ax_profile_y.plot(y_profile, np.arange(len(y_profile)), 'g-', linewidth=2, label='Профиль по Y')
        ax_profile_y.axhline(y=centroid_y, color='red', linestyle='--', linewidth=2)
        ax_profile_y.set_ylabel('Координата Y')
        ax_profile_y.set_xlabel('Интенсивность')
        ax_profile_y.set_title(f'Профиль интенсивности при X={int(centroid_x)}')
        ax_profile_y.grid(True, alpha=0.3)
        ax_profile_y.legend()

        # Убираем лишние оси
        self.fig.add_subplot(self.gs[0, 0]).axis('off')
        self.fig.add_subplot(self.gs[0, 3]).axis('off')
        self.fig.add_subplot(self.gs[3, 0]).axis('off')
        self.fig.add_subplot(self.gs[3, 3]).axis('off')

        plt.tight_layout()

        self.plot_canvas.draw()
        self.plot_canvas.flush_events()

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Beam Centroid', 'Plots'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
