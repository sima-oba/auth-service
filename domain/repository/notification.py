from abc import ABC, abstractmethod

from ..model import User


class INotifier(ABC):
    @abstractmethod
    def send_owner_email_verification(self, user: User, code: str):
        pass

    @abstractmethod
    def send_email_verification(self, user: User, code: str):
        pass

    @abstractmethod
    def send_reset_password(self, user: User, code: str):
        pass
