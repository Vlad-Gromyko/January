from abc import ABC, abstractmethod

from application.widgets.maskwidget import MaskLabel


class Event:
    def __init__(self, name: str, value=None):
        self._name = name
        self._value = value

    def get_value(self):
        return self._value

    def get_name(self) -> str:
        return self._name


class Service(ABC):
    def __init__(self):
        self.event_bus = None
        self.events_reactions = {}
        self.name = 'Abstract'

        self.saved_state = False

        self.events_reactions['Load'] = lambda event: self.set_project(event.get_value())


    def set_project(self, path):
        pass

    def add_right_click_menu(self, mask_label: MaskLabel, label: str, command):
        mask_label.label.menu.add_command(label=label, command=command)

    def raise_event(self, event: Event):
        if event.get_name() in self.events_reactions.keys():
            self.events_reactions[event.get_name()](event)



class EventBus:
    def __init__(self):
        self.services = {}


    def start(self):
        for service_name in self.services.keys():
            self.services[service_name].start_service()

    def open_project(self, new_project):
        for service_name in self.services.keys():
            self.services[service_name].open_project(new_project)

    def add_service(self, service: Service):
        self.services[service.name] = service
        service.event_bus = self

    def get_field(self, name: str):
        answer = None
        if name in self.services.keys():
            answer = self.services[name]

        return answer


    def raise_event(self, event: Event):
        print(event.get_name())
        answer = []
        for service_name in self.services.keys():
            answer.append(self.services[service_name].raise_event(event))
        return all(answer)
