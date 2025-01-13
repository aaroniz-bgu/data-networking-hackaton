from abc import ABC, abstractmethod


class AbstractServer(ABC):
    @abstractmethod
    def start(self):
        pass

    @abstractmethod
    def serve(self):
        pass

    @abstractmethod
    def stop(self):
        pass
