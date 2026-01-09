from abc import ABC, abstractmethod
from typing import Any, Dict
from ..llm_factory import llm_factory
from ..config import config

class BaseAgent(ABC):
    def __init__(self, role_name: str):
        self.role_name = role_name
        self.cfg = config.get_model_map().get(role_name.lower(), {})
        self.llm = llm_factory.get_llm(
            self.cfg.get('provider', 'groq'),
            self.cfg.get('model', 'llama-3.3-70b-versatile')
        )

    @abstractmethod
    def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        pass