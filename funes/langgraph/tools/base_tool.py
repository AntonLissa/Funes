from abc import ABC, abstractmethod

class BaseTool(ABC):

    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @abstractmethod
    def run(self):
        pass


