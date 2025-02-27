from abc import ABC, abstractmethod

from application.widgets.maskwidget import MaskLabel

from tkinterdnd2 import TkinterDnD, DND_ALL


class Event:
    def __init__(self, name: str, value=None):
        self._name = name
        self._value = value

    def get_value(self):
        return self._value

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


class EventBus:
    def __init__(self):
        self.services = []

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
        print(name)
        answer = None
        for service_name in self.services:
            if name in service_name.fields.keys():
                answer = service_name.fields[name]

        return answer

    def raise_event(self, event: Event):
        print(event.get_name())
        answer = []
        for service_name in self.services:
            answer.append(service_name.raise_event(event))
        return all(answer)
