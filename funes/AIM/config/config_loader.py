from pathlib import Path
import yaml

class ConfigLoader:
    def __init__(self, base_path: Path = None):
        self.base_path = base_path or Path(__file__).parent
        self.config = {}
        self.api_key = None

    def load_api_key(self, filename="api_key.txt"):
        key_path = self.base_path / filename
        if not key_path.exists():
            raise FileNotFoundError(f"API key file not found at {key_path}")
        self.api_key = key_path.read_text().strip()
        return self.api_key

    def load_yaml(self, filename="llm_config.yaml"):
        yaml_path = self.base_path / filename
        if not yaml_path.exists():
            raise FileNotFoundError(f"Config file not found at {yaml_path}")
        with open(yaml_path, "r", encoding="utf-8") as f:
            self.config = yaml.safe_load(f)
        return self.config
