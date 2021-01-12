
from abc import ABC, abstractmethod


class BaseAlarm(ABC):

    @abstractmethod
    def send(self, name, msg):
        pass
