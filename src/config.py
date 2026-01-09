import yaml
import os
import random
from typing import Dict, Any, List
from dotenv import load_dotenv

class Config:
    def __init__(self, config_path: str = "config.yaml"):
        load_dotenv()
        self._config = {}
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                self._config = yaml.safe_load(f)
        
        # Default Fallback Map if config.yaml is missing
        if not self._config.get('model_map'):
            self._config['model_map'] = {
                "manager": {"provider": "groq", "model": "llama-3.3-70b-versatile"},
                "architect": {"provider": "groq", "model": "llama-3.3-70b-versatile"},
                "developer": {"provider": "groq", "model": "llama-3.3-70b-versatile"},
                "deployer": {"provider": "groq", "model": "llama-3.3-70b-versatile"}
            }

        self._api_keys = {
            "groq": self._parse_env_keys("GROQ_API_KEYS") or self._parse_env_keys("GROQ_API_KEY"),
            "google": self._parse_env_keys("GOOGLE_API_KEYS"),
            "openai": self._parse_env_keys("OPENAI_API_KEY"),
        }
    
    def _parse_env_keys(self, env_var: str) -> List[str]:
        value = os.getenv(env_var, "")
        if not value: return []
        return [k.strip() for k in value.split(",") if k.strip()]
        
    def get_model_map(self) -> Dict[str, Any]:
        return self._config.get('model_map', {})

    def get_logging_config(self) -> Dict[str, Any]:
        return self._config.get('logging', {})

    def get_api_key(self, provider: str) -> str:
        keys = self._api_keys.get(provider.lower(), [])
        if keys: return random.choice(keys)
        return ""

config = Config()