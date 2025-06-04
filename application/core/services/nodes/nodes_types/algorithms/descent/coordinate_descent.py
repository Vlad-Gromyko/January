import numpy
import numpy as np
import customtkinter as ctk
from application.core.services.nodes.node import INode


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Число Итераций', self.palette['NUM'])

        self.add_enter_socket('Шаг', self.palette['NUM'])

        self.add_enter_socket('Решение', self.palette['vector1d'])

        self.add_enter_socket('Метрика', self.palette['NUM'])

        self.add_output_socket('Индекс', self.palette['NUM'])
        self.add_output_socket('Индекс Шага', self.palette['NUM'])

        self.add_output_socket('Решение', self.palette['vector1d'])

        self.add_output_socket('Метрика', self.palette['SIGNAL'])
        self.add_output_socket('Решение +- Шаг', self.palette['vector1d'])
        self.add_output_socket('После Шага', self.palette['SIGNAL'])

        self.add_output_socket('Триггер Шага', self.palette['SIGNAL'])
        self.add_output_socket('Шаг', self.palette['NUM'])

        self.add_output_socket('После Итерации', self.palette['SIGNAL'])

        self.previous = None

        self.load_data = kwargs
        self.strong_control = True

    def execute(self):
        arguments = self.get_func_inputs()

        solution = np.asarray(arguments['Решение'])
        num = len(solution)

        for i in range(0, int(arguments['Число Итераций'])):
            self.output_sockets['Индекс'].set_value(i)
            arguments = self.get_func_inputs()
            step = arguments['Шаг']

            for j in range(num):
                self.output_sockets['Индекс Шага'].set_value(j)
                arguments = self.get_func_inputs()
                solution = np.asarray(arguments['Решение'])
                step = arguments['Шаг']

                print(step)

                u_plus = np.copy(solution)
                u_plus[j] = solution[j] + step
                u_minus = np.copy(solution)
                u_minus[j] = solution[j] - step

                print(solution)
                print(u_plus)
                print(u_minus)

                self.output_sockets['Решение +- Шаг'].set_value(list(u_plus))
                self.output_sockets['Метрика'].set_value(True)

                arguments = self.get_func_inputs()
                m_plus = np.asarray(arguments['Метрика'])

                self.output_sockets['Решение +- Шаг'].set_value(list(u_minus))
                self.output_sockets['Метрика'].set_value(True)

                arguments = self.get_func_inputs()
                m_minus = np.asarray(arguments['Метрика'])

                if m_plus <= m_minus:
                    self.output_sockets['Решение'].set_value(list(u_plus))
                else:
                    self.output_sockets['Решение'].set_value(list(u_minus))

                self.output_sockets['После Шага'].set_value(True)

            self.output_sockets['Шаг'].set_value(step)
            self.output_sockets['Триггер Шага'].set_value(True)

            self.output_sockets['После Итерации'].set_value(True)

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Координатный спуск', 'gradient'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
