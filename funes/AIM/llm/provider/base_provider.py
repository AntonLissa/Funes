from abc import ABC, abstractmethod
from typing import Optional

class BaseProvider(ABC):
    @abstractmethod
    def call(self, model_name: str, system_prompt: str, user_prompt: str, temperature: float = 0) -> Optional[str]:
        pass
