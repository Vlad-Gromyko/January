import numpy
import numpy as np
import customtkinter as ctk
from application.core.services.nodes.node import INode
import datetime

def random_zero(vector, zero_ratio=0.3):
    """
    Обнуляет случайные элементы вектора с использованием NumPy.

    Args:
        vector: входной вектор (list или numpy array)
        zero_ratio: доля элементов для обнуления (0-1)

    Returns:
        Вектор с обнуленными элементами
    """
    arr = np.array(vector)

    if zero_ratio == 0:
        return arr

    if len(arr) == 0:
        return arr

    # Не даем обнулить все элементы
    zero_ratio = min(zero_ratio, 0.99)

    # Создаем маску для обнуления
    mask = np.random.random(len(arr)) < zero_ratio

    # Проверяем, что не обнуляем все элементы
    if np.all(mask):
        # Отменяем обнуление для одного случайного элемента
        idx = np.random.randint(0, len(arr))
        mask[idx] = False

    # Применяем маску
    result = arr.copy()
    result[mask] = 0

    return result

class Node(INode):
    def __init__(self, special_id, config, editor, canvas, x, y, control, text, theme, **kwargs):
        super().__init__(special_id, config, editor, canvas, x, y, control, text, theme)

        self.special_id = special_id

        self.add_enter_socket('Число Итераций', self.palette['NUM'])
        self.add_enter_socket('Целевое Распределение', self.palette['vector1d'])
        self.add_enter_socket('Скорость', self.palette['NUM'])

        self.add_enter_socket('Решение', self.palette['vector1d'])

        self.add_enter_socket('Интенсивности', self.palette['vector1d'])

        self.add_output_socket('Индекс', self.palette['NUM'])
        self.add_output_socket('Метрика', self.palette['SIGNAL'])

        self.add_output_socket('Решение', self.palette['vector1d'])


        self.add_output_socket('После Итерации', self.palette['SIGNAL'])




        self.previous = None

        self.load_data = kwargs
        self.strong_control = True






        self.design = []

        self.intensities_history = []
        self.u_history = []

        self.velocity = 1

        self.weights_history = []

        self.norm_velocity = None


    def iteration(self, weights):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        print(f"The time is {now}")

        self.output_sockets['Решение'].set_value(list(weights))

        self.output_sockets['Метрика'].set_value(True)

        arguments = self.get_func_inputs()

        values = np.asarray(arguments['Интенсивности'])

        u = self.uniformity(values / self.design)
        self.u_history.append(u)

        self.intensities_history.append(values)
        self.weights_history.append(weights)
        self.output_sockets['После Итерации'].set_value(True)


    def execute(self):

        self.intensities_history = []
        self.u_history = []
        self.design = []

        self.norm_velocity = None

        self.weights_history = []

        arguments = self.get_func_inputs()
        self.velocity = arguments['Скорость']



        self.design = np.asarray(arguments['Целевое Распределение'])

        weights = arguments['Решение']
        self.iteration(weights)


        for k in range(0, int(arguments['Число Итераций'])):
            self.output_sockets['Индекс'].set_value(k)
            values = self.intensities_history[-1]



            gradient = (self.design / np.max(self.design) - values)
            norm = np.linalg.norm(gradient)
            if self.norm_velocity is None:
                self.norm_velocity = norm
            else:
                self.norm_velocity = min(self.norm_velocity, norm)

            gradient = gradient / self.norm_velocity

            print(np.linalg.norm(gradient))

            weights = weights + self.velocity * self.norm_velocity * gradient

            print('NV  ',self.norm_velocity, norm)

            self.iteration(weights)

        if 'go' in self.output_sockets.keys():
            self.output_sockets['go'].set_value(True)

    @staticmethod
    def uniformity(values):
        return 1 - (np.max(values) - np.min(values)) / (np.max(values) + np.min(values))

    @staticmethod
    def create_info():
        return Node, 'True Old', 'gradient'

    def prepare_save_spec(self):
        data = {}
        saves = self.saves_dict()
        save = {**data, **saves}
        return __file__, self.x, self.y, save, self.special_id, self.with_signals
