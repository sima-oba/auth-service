from abc import ABC, abstractmethod

from ..model import Owner


class IProtocolPublisher(ABC):
    @abstractmethod
    def send_new_owner(self, owner: Owner):
        pass
