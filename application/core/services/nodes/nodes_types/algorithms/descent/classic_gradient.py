import numpy
import numpy as np

from application.core.services.nodes.node import INode


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Число Итераций', self.palette['NUM'])
        self.add_enter_socket('Скорость', self.palette['NUM'])

        self.add_enter_socket('Решение', self.palette['vector1d'])
        self.add_enter_socket('Шаг Градиента', self.palette['NUM'])

        self.add_enter_socket('Метрика', self.palette['NUM'])

        self.add_output_socket('Индекс', self.palette['NUM'])

        self.add_output_socket('Решение', self.palette['vector1d'])
        self.add_output_socket('Градиент', self.palette['vector1d'])

        self.add_output_socket('Триггер Градиента', self.palette['SIGNAL'])
        self.add_output_socket('Градиент(+-)', self.palette['vector1d'])

        self.add_output_socket('Индекс Градиента', self.palette['NUM'])
        self.add_output_socket('Триггер Скорости', self.palette['SIGNAL'])
        self.add_output_socket('Скорость', self.palette['NUM'])

        self.add_output_socket('Триггер Шага', self.palette['SIGNAL'])
        self.add_output_socket('Шаг Градиента', self.palette['NUM'])

        self.add_output_socket('После Итерации', self.palette['SIGNAL'])

        self.load_data = kwargs
        self.strong_control = True

    def execute(self):
        arguments = self.get_func_inputs()

        num = len(arguments['Решение'])
        gradient = [0 for i in range(num)]

        for i in range(0, int(arguments['Число Итераций'])):
            arguments = self.get_func_inputs()
            self.output_sockets['Индекс'].set_value(i)

            u = np.asarray(arguments['Решение'].copy())
            velocity = arguments['Скорость']

            delta = arguments['Шаг Градиента']

            u_plus = numpy.copy(u)
            u_minus = numpy.copy(u)

            for j in range(num):
                print()
                print()
                print(j)
                self.output_sockets['Индекс Градиента'].set_value(j)

                u_plus[j] = u_plus[j] + delta
                u_minus[j] = u_minus[j] - delta

                self.output_sockets['Градиент(+-)'].set_value(list(u_plus))
                self.output_sockets['Триггер Градиента'].set_value(True)

                arguments = self.get_func_inputs()
                m_plus = arguments['Метрика']
                print(m_plus)

                self.output_sockets['Градиент(+-)'].set_value(list(u_minus))
                self.output_sockets['Триггер Градиента'].set_value(True)

                arguments = self.get_func_inputs()
                m_minus = arguments['Метрика']
                print(m_minus)

                gradient[j] = (m_plus - m_minus) / 2 / delta

                print('U-plus ', u_plus)
                print('U-minus ', u_minus)

                u_plus[j] = u_plus[j] - delta
                u_minus[j] = u_minus[j] + delta

                print('grad', gradient)
            gradient = np.asarray(gradient)

            gradient  = gradient / np.linalg.norm(gradient)
            print(gradient)
            result = list(u + velocity * gradient)

            self.output_sockets['Решение'].set_value(result)
            self.output_sockets['Градиент'].set_value(list(gradient))

            self.output_sockets['Скорость'].set_value(velocity)
            self.output_sockets['Триггер Скорости'].set_value(True)

            self.output_sockets['Шаг Градиента'].set_value(delta)
            self.output_sockets['Триггер Шага'].set_value(True)


            self.output_sockets['После Итерации'].set_value(True)
            self.output_sockets['После Итерации'].set_value(None)


        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Градиентный спуск', 'gradient'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
