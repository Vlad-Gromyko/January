from math import floor

import numpy
import numpy as np
import customtkinter as ctk
from application.core.services.nodes.node import INode


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Число Итераций', self.palette['NUM'])

        self.add_enter_socket('Скорость', self.palette['NUM'])
        self.add_enter_socket('Шаг', self.palette['NUM'])
        self.add_enter_socket('Бета 1', self.palette['NUM'])
        self.add_enter_socket('Бета 2', self.palette['NUM'])
        self.add_enter_socket('Лямбда', self.palette['NUM'])
        self.add_enter_socket('Эпсилон', self.palette['NUM'])
        self.add_enter_socket('Распад', self.palette['NUM'])

        self.add_enter_socket('Решение', self.palette['vector1d'])
        self.add_enter_socket('Метрика', self.palette['NUM'])

        self.add_output_socket('Индекс', self.palette['NUM'])

        self.add_output_socket('Решение', self.palette['vector1d'])

        self.add_output_socket('Метрика', self.palette['SIGNAL'])
        self.add_output_socket('Решение +- Шаг', self.palette['vector1d'])

        self.add_output_socket('Триггер Скорости', self.palette['SIGNAL'])

        self.add_output_socket('Скорость', self.palette['NUM'])

        self.add_output_socket('Триггер Шага', self.palette['SIGNAL'])
        self.add_output_socket('Шаг', self.palette['NUM'])

        self.add_output_socket('После Итерации', self.palette['SIGNAL'])

        self.previous = None

        self.load_data = kwargs
        self.strong_control = True

        self.widget_width = 400
        self.widget_height = 200
        frame_widgets = ctk.CTkFrame(self.canvas, width=self.widget_width, height=self.widget_height)
        self.frame_IDs['widgets'] = self.canvas.create_window(self.x, self.y, window=frame_widgets,
                                                              anchor=ctk.NW, width=self.widget_width,
                                                              height=self.widget_height)

        values = ['Gradient', 'AdaGrad', 'RMSProp', 'Adam', 'AdaMax', 'AdamW']

        self.combo = ctk.CTkComboBox(frame_widgets, values=values)
        self.combo.set('AdaGrad')
        self.combo.grid(row=0, column=1, padx=5, pady=5)

        ctk.CTkLabel(frame_widgets, text='Стратегия').grid(row=0, column=0, padx=5, pady=5)
        ctk.CTkLabel(frame_widgets, text='Планировщик').grid(row=1, column=0, padx=5, pady=5)

        values_lr = ['Hyberbolical', 'Exponential', 'Constant']

        self.combo_lr = ctk.CTkComboBox(frame_widgets, values=values_lr)
        self.combo_lr.set('Hyberbolical')
        self.combo_lr.grid(row=1, column=1, padx=5, pady=5)

        self.step = 0.01
        self.velocity = 1
        self._lambda = 0.01
        self.g = 0
        self.epsilon = 0.00000001
        self.m = 0
        self.v = 0
        self.m_hat = 0
        self.v_hat = 0
        self.beta_1 = 0.99
        self.beta_2 = 0.999
        self.decay = 100

        self.plan = 1

        self.check_reg = ctk.StringVar(value="off")
        self.checkbox_reg = ctk.CTkCheckBox(frame_widgets, text="Регуляризация",
                                            variable=self.check_reg, onvalue="on", offvalue="off")
        self.checkbox_reg.grid(row=2, column=1, padx=5, pady=5)

        self.check_step = ctk.StringVar(value="off")
        self.checkbox_step = ctk.CTkCheckBox(frame_widgets, text="Спупенчатость",
                                             variable=self.check_step, onvalue="on", offvalue="off")
        self.checkbox_step.grid(row=3, column=1, padx=5, pady=5)

    def execute(self):
        arguments = self.get_func_inputs()

        self.step = arguments['Шаг']
        self.velocity = arguments['Скорость']
        self._lambda = arguments['Лямбда']
        self.g = 0
        self.epsilon = arguments['Эпсилон']
        self.m_hat = 0
        self.v_hat = 0
        self.m = 0
        self.v = 0
        self.beta_1 = arguments['Бета 1']
        self.beta_2 = arguments['Бета 2']
        self.decay = arguments['Распад']

        num = len(arguments['Решение'])

        self.previous = np.asarray(arguments['Решение'])

        for i in range(0, int(arguments['Число Итераций'])):
            arguments = self.get_func_inputs()
            self.output_sockets['Индекс'].set_value(i)

            steps = np.random.choice([-1, 1], size=num)

            u = np.asarray(arguments['Решение'].copy())

            u_plus = u + steps * self.step
            u_minus = u - steps * self.step

            self.output_sockets['Решение +- Шаг'].set_value(list(u_plus))
            self.output_sockets['Метрика'].set_value(True)

            arguments = self.get_func_inputs()
            m_plus = arguments['Метрика']

            self.output_sockets['Решение +- Шаг'].set_value(list(u_minus))
            self.output_sockets['Метрика'].set_value(True)

            arguments = self.get_func_inputs()
            m_minus = arguments['Метрика']

            gradient = (m_plus - m_minus) / (2 * self.step) * steps

            if self.combo.get() == 'Gradient':
                prognosis = self.velocity * gradient
            elif self.combo.get() == 'AdaGrad':
                self.g = self.g + gradient ** 2

                prognosis = self.velocity * gradient / np.sqrt(self.g + self.epsilon)
            elif self.combo.get() == 'RMSProp':
                if i == 0:
                    self.g = gradient ** 2
                else:
                    self.g = self.g * self.beta_1 + (1 - self.beta_1) * gradient ** 2

                prognosis = self.velocity * gradient / np.sqrt(self.g + self.epsilon)

            elif self.combo.get() == 'Adam':
                if i == 0:
                    self.m = gradient
                    self.v = gradient ** 2
                else:
                    self.m = self.m * self.beta_1 + (1 - self.beta_1) * gradient
                    self.v = self.v * self.beta_2 + (1 - self.beta_2) * gradient ** 2

                self.m_hat = self.m / (1 - self.beta_1 ** (i + 1))
                self.v_hat = self.v / (1 - self.beta_2 ** (i + 1))

                prognosis = self.m_hat / (np.sqrt(self.v_hat) + self.epsilon)

            else:
                prognosis = 0

            if self.check_step.get() == 'on':
                ratio = i // self.decay
            else:
                ratio = i / self.decay

            if self.combo_lr.get() == 'Hyberbolical':
                self.plan = 1 / (1 + ratio)
            elif self.combo_lr.get() == 'Exponential':
                self.plan = np.exp(-ratio)
            elif self.combo_lr.get() == 'Constant':
                self.plan = 1

            result = u - prognosis * self.plan

            if self.check_reg.get() == 'on':
                result = result - self._lambda * u

            result = list(result)

            self.previous = u

            self.output_sockets['Решение'].set_value(result)

            self.output_sockets['Скорость'].set_value(self.velocity * self.plan)
            self.output_sockets['Триггер Скорости'].set_value(True)

            self.output_sockets['Шаг'].set_value(self.step)
            self.output_sockets['Триггер Шага'].set_value(True)

            self.output_sockets['После Итерации'].set_value(True)

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Суб-Рандомный Градиентный спуск', 'gradient'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
