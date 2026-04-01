from pathlib import Path
import yaml
import os

class ConfigLoader:
    def __init__(self, base_path: Path = None):
        self.base_path = base_path or Path(__file__).parent
        self.config = {}
        self.api_key = None

    def load_api_key(self, env_var_name="GROQ_API_KEY"):
        """
        Carica l'API key da variabile d'ambiente, fallback a file locale.
        """
        key = os.getenv(env_var_name)
        if key:
            self.api_key = key.strip()
            return self.api_key


        raise FileNotFoundError(
            f"API key not found. Tried env var '{env_var_name}'"
        )

    def load_yaml(self, filename="llm_config.yaml"):
        yaml_path = self.base_path / filename
        if not yaml_path.exists():
            raise FileNotFoundError(f"Config file not found at {yaml_path}")
        with open(yaml_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
        return self.config
