"""Configuration utilities."""
from typing import Dict, Any
import json
import os

class Config:
    """Configuration manager."""
    
    def __init__(self, config_file: str = "config.json"):
        self.config_file = config_file
        self.config: Dict[str, Any] = {}
        self.load()
    
    def load(self) -> None:
        """Load configuration from file."""
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self.config = json.load(f)
    
    def save(self) -> None:
        """Save configuration to file."""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        self.config[key] = value
        self.save()