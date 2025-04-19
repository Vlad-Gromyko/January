from abc import ABC, abstractmethod

from scipy.constants import value

from application.widgets.maskwidget import MaskLabel

from tkinterdnd2 import TkinterDnD, DND_ALL
import os, struct, shutil

class Event:
    def __init__(self, name: str, value=None):
        self._name = name
        self._value = value

    def get_value(self):
        return self._value

    def set_value(self, value):
        self._value = value

    def get_name(self) -> str:
        return self._name


class Service(ABC, TkinterDnD.DnDWrapper):
    def __init__(self):
        self.event_bus = None
        self.events_reactions = {}
        self.name = 'Abstract'

        self.saved_state = False

        self.fg_color = None

        self.events_reactions['Load'] = lambda event: self.set_project(event.get_value())
        self.events_reactions['Drop Start'] = lambda event: self.drop_start()
        self.events_reactions['Drop End'] = lambda event: self.drop_end()
        self.events_reactions['Save Project'] = lambda event: self.save_project(event.get_value())

        self.fields = {}

    def drop_start(self):
        pass

    def drop_end(self):
        pass

    def set_project(self, path):
        pass

    def add_right_click_menu(self, mask_label: MaskLabel, label: str, command):
        mask_label.label.menu.add_command(label=label, command=command)

    def raise_event(self, event: Event):
        if event.get_name() in self.events_reactions.keys():
            self.events_reactions[event.get_name()](event)

    def save_project(self, path):
        pass


class EventBus:
    def __init__(self):
        self.services = []
        self.project_path = None

    def start(self):
        for service_name in self.services:
            service_name.start_service()

    def open_project(self, new_project):
        for service_name in self.services:
            service_name.open_project(new_project)

    def add_service(self, service: Service):
        self.services.append(service)
        service.event_bus = self

    def get_field(self, name: str):
        answer = None
        for service_name in self.services:
            if name in service_name.fields.keys():
                answer = service_name.fields[name]

        return answer

    def raise_event(self, event: Event):
        if event.get_name() == 'Load':
            self.project_path = event.get_value()
            #print(event.get_value())
            name = event.get_value()
            #hyperion_to_folder(event.get_value(), event.get_value().split('.')[0])
            #event.set_value(event.get_value().split('.')[0])


        #print(event.get_name())
        answer = []
        for service_name in self.services:
            answer.append(service_name.raise_event(event))
        if event.get_name() == 'Save Project':
            self.raise_event(Event('Show Splash'))
            #folder_to_hyperion(event.get_value(), event.get_value() + '.hyperion')
            #shutil.rmtree(event.get_value())
            print('Saved')
        #if event.get_name() == 'Load':
           # shutil.rmtree(event.get_value().split('.')[0])
            self.raise_event(Event('Hide Splash'))
        return all(answer)


def folder_to_hyperion(folder_path, output_file):
    with open(output_file, 'wb') as f_out:
        # Записываем сигнатуру формата (например, "VLAD")
        f_out.write(b'HYPE')

        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, folder_path)

                # Читаем содержимое файла
                with open(file_path, 'rb') as f_in:
                    content = f_in.read()

                # Записываем:
                # 1. Длину пути (4 байта)
                # 2. Сам путь (в UTF-8)
                # 3. Длину содержимого (4 байта)
                # 4. Само содержимое
                path_bytes = rel_path.encode('utf-8')
                f_out.write(struct.pack('I', len(path_bytes)))  # Длина пути
                f_out.write(path_bytes)  # Путь
                f_out.write(struct.pack('I', len(content)))  # Длина данных
                f_out.write(content)


def hyperion_to_folder(input_file, output_folder):
    os.makedirs(output_folder, exist_ok=True)

    with open(input_file, 'rb') as f_in:
        # Проверяем сигнатуру
        signature = f_in.read(4)
        if signature != b'HYPE':
            raise ValueError("Неверный формат файла!")

        while True:
            # Читаем путь
            len_path_bytes = f_in.read(4)
            if not len_path_bytes:
                break  # Конец файла

            len_path = struct.unpack('I', len_path_bytes)[0]
            path = f_in.read(len_path).decode('utf-8')

            # Читаем данные
            len_content = struct.unpack('I', f_in.read(4))[0]
            content = f_in.read(len_content)

            # Сохраняем файл
            full_path = os.path.join(output_folder, path)
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
            with open(full_path, 'wb') as f_out:
                f_out.write(content)
