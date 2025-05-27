import numpy
import numpy as np

from application.core.services.nodes.node import INode


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Число Итераций', self.palette['NUM'])
        self.add_enter_socket('Скорость', self.palette['NUM'])
        self.add_enter_socket('Шаг', self.palette['NUM'])

        self.add_enter_socket('Решение', self.palette['vector1d'])


        self.add_enter_socket('Метрика', self.palette['NUM'])

        self.add_output_socket('Индекс', self.palette['NUM'])

        self.add_output_socket('Решение', self.palette['vector1d'])
        self.add_output_socket('Решение +- Шаг', self.palette['vector1d'])


        self.add_output_socket('Триггер Скорости', self.palette['SIGNAL'])
        self.add_output_socket('Скорость', self.palette['NUM'])

        self.add_output_socket('Триггер Шага', self.palette['SIGNAL'])
        self.add_output_socket('Шаг', self.palette['NUM'])

        self.add_output_socket('После Итерации', self.palette['SIGNAL'])

        self.load_data = kwargs
        self.strong_control = True

    def execute(self):
        arguments = self.get_func_inputs()

        num = len(arguments['Решение'])

        for i in range(0, int(arguments['Число Итераций'])):
            arguments = self.get_func_inputs()
            self.output_sockets['Индекс'].set_value(i)

            amp = arguments['Шаг']

            steps = np.asarray(amp if np.random.rand() < 0.5 else -1 * amp for i in range(num))

            u = np.asarray(arguments['Решение'].copy())

            u_plus = u + steps
            u_minus = u - steps

            self.output_sockets['Решение +- Шаг'].set_value(list(u_plus))
            self.output_sockets['Метрика'].set_value(True)

            arguments = self.get_func_inputs()
            m_plus = arguments['Метрика']
            print(m_plus)

            self.output_sockets['Решение +- Шаг'].set_value(list(u_minus))
            self.output_sockets['Метрика'].set_value(True)

            arguments = self.get_func_inputs()
            m_minus = arguments['Метрика']
            print(m_minus)

            velocity = arguments['Скорость']

            gradient = steps * (m_plus - m_minus)

            gradient  = gradient / np.linalg.norm(gradient)

            result = u - velocity * gradient
            result = list(result)

            self.output_sockets['Решение'].set_value(result)

            self.output_sockets['Скорость'].set_value(velocity)
            self.output_sockets['Триггер Скорости'].set_value(True)

            self.output_sockets['Шаг Градиента'].set_value(amp)
            self.output_sockets['Триггер Шага'].set_value(True)

            self.output_sockets['После Итерации'].set_value(True)

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Стохастический Градиентный спуск', 'gradient'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
