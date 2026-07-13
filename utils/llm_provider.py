from abc import ABC, abstractmethod
from pydantic import BaseModel

class LLMProvider(ABC):
    """
    Abstract Base Class defining the contract for all LLM providers in the application.
    Enables dependency injection and swapping of the underlying LLM provider.
    """
    @abstractmethod
    def generate_structured_output(self, prompt: str, response_schema: type[BaseModel], temperature: float = 0.2) -> BaseModel:
        """
        Executes a prompt against the model and returns a validated Pydantic model response.
        """
        pass
