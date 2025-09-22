import customtkinter as ctk
import numpy as np
import plotly.express as px
import pandas as pd
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg)
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize

from application.core.services.nodes.node import INode
from application.core.utility.mask import Mask


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('[[X]]', self.palette['vector1d'])
        self.add_enter_socket('[Y]', self.palette['vector1d'])

        self.load_data = kwargs
        self.widget_width = 100
        self.widget_height = 100
        frame_widgets = ctk.CTkFrame(self.canvas, width=self.widget_width, height=self.widget_height)
        self.frame_IDs['widgets'] = self.canvas.create_window(self.x, self.y, window=frame_widgets,
                                                              anchor=ctk.NW, width=self.widget_width,
                                                              height=self.widget_height)

        self.fig = None

        cmaps = ['viridis', 'plasma', 'inferno', 'magma', 'cividis', 'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone',
                 'pink',
                 'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
                 'hot', 'afmhot', 'gist_heat', 'copper']

        self.combo = ctk.CTkComboBox(frame_widgets, values=cmaps, width=100, height=20)
        self.combo.set('viridis')
        self.combo.grid()

    def execute(self):
        arguments = self.get_func_inputs()

        x = arguments['[[X]]']
        y = arguments['[Y]']

        df = pd.DataFrame(x)
        df['Function_Value'] = y
        # Сортируем по УБЫВАНИЮ - большие значения первыми
        df_sorted = df.sort_values('Function_Value', ascending=False)

        fig, ax = plt.subplots(figsize=(14, 8), facecolor='#0E1117')

        norm = plt.Normalize(vmin=df['Function_Value'].min(), vmax=df['Function_Value'].max())
        cmap = plt.get_cmap(self.combo.get() + '_r')  # Получаем colormap

        # Рисуем в ОБРАТНОМ порядке: от последнего к первому
        for i in range(len(df_sorted)-1, -1, -1):
            row = df_sorted.iloc[i]
            values = row.drop('Function_Value').values
            color = cmap(norm(row['Function_Value']))  # Используем cmap
            ax.plot(range(len(values)), values, color=color, alpha=0.8, linewidth=1.2)

        ax.set_title('Параллельные координаты (большие значения под малыми)',
                     color='white', fontsize=14, pad=20)
        ax.grid(True, alpha=0.2, color='gray')
        ax.set_xticks(range(len(df_sorted.columns) - 1))
        ax.set_xticklabels([f'Feature {i+1}' for i in range(len(df_sorted.columns) - 1)])

        # Colorbar
        sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)  # Используем ту же cmap
        sm.set_array([])
        cbar = plt.colorbar(sm, ax=ax)
        cbar.set_label('Значение функции', color='white', fontsize=12)

        if ax.get_legend() is not None:
            ax.get_legend().remove()

        plt.tight_layout()
        plt.show()

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'ПК', 'Plots'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
