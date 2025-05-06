import numpy as np

from application.core.services.nodes.node import INode


class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Число Итераций', self.palette['NUM'])
        self.add_enter_socket('Скорость', self.palette['NUM'])

        self.add_enter_socket('U', self.palette['vector1d'])
        self.add_enter_socket('Шаг', self.palette['NUM'])

        self.add_enter_socket('Метрика', self.palette['NUM'])

        self.add_output_socket('U', self.palette['vector1d'])
        self.add_output_socket('dU', self.palette['vector1d'])

        self.add_output_socket('Функция', self.palette['SIGNAL'])
        self.add_output_socket('U +- dU', self.palette['vector1d'])

        self.add_output_socket('Индекс', self.palette['NUM'])
        self.add_output_socket('Скорость', self.palette['NUM'])
        self.add_output_socket('После Итерации', self.palette['SIGNAL'])

        self.load_data = kwargs
        self.strong_control = True

    def execute(self):
        arguments = self.get_func_inputs()

        sigma = arguments['Шаг']
        num = len(arguments['U'])

        for i in range(0, int(arguments['Число Итераций'])):
            arguments = self.get_func_inputs()

            u = np.asarray(arguments['U'].copy())
            du = np.asarray([sigma if np.random.rand() < 0.5 else -1 * sigma for i in range(num)])
            self.output_sockets['dU'].set_value(list(du))

            u_plus = list(u + du)
            u_minus = list(u - du)

            self.output_sockets['Индекс'].set_value(i)

            self.output_sockets['U +- dU'].set_value(u_plus)
            self.output_sockets['Функция'].set_value(True)

            arguments = self.get_func_inputs()
            m_plus = arguments['Метрика']

            self.output_sockets['Функция'].set_value(None)

            self.output_sockets['U +- dU'].set_value(u_minus)
            self.output_sockets['Функция'].set_value(True)

            arguments = self.get_func_inputs()
            m_minus = arguments['Метрика']

            self.output_sockets['Функция'].set_value(None)

            arguments = self.get_func_inputs()
            velocity = arguments['Скорость']

            result = list(u + velocity * du * (m_plus - m_minus))

            self.output_sockets['U'].set_value(result)
            self.output_sockets['Скорость'].set_value(velocity)

            self.output_sockets['После Итерации'].set_value(True)
            self.output_sockets['После Итерации'].set_value(None)


        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def create_info():
        return Node, 'Градиентный спуск M+M-', 'gradient'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
