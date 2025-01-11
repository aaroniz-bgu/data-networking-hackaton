from abc import ABC, abstractmethod


class AbstractServer(ABC):
    @abstractmethod
    def serve(self):
        pass

    @abstractmethod
    def stop(self):
        pass
