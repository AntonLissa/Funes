from abc import ABC, abstractmethod

class BaseChunker(ABC):
    @abstractmethod
    def chunk(self, text: str) -> list[str]:
        pass

    @abstractmethod
    def load_document(self, file_path: str) -> list[str]:
        pass