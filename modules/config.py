"""Configuration management for websum."""
import os
import yaml
from typing import Dict, Any

def load_config(config_file: str = "config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file."""
    if not os.path.exists(config_file):
        return get_default_config()
    
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    return config

def get_default_config() -> Dict[str, Any]:
    """Get default configuration."""
    return {
        "output": {
            "dir": "./output",
            "cache_file": "url_cache.json"
        },
        "crawler": {
            "max_buffer_size": 1000000,
            "chunk_size": 524288,
            "stream_mode": True,
            "page_limit": None
        },
        "content": {
            "word_count_threshold": 10,
            "exclude_navigation": True,
            "clean_markdown": True,
            "process_code_blocks": True
        },
        "rate_limit": {
            "delay_seconds": 1.0,
            "max_retries": 3,
            "backoff_factor": 2.0
        }
    }

def update_environment(config: Dict[str, Any]) -> None:
    """Update environment variables based on configuration."""
    os.environ["CRAWL4AI_MAX_BUFFER_SIZE"] = str(config["crawler"]["max_buffer_size"])
    os.environ["CRAWL4AI_CHUNK_SIZE"] = str(config["crawler"]["chunk_size"])
    os.environ["CRAWL4AI_STREAM_MODE"] = str(config["crawler"]["stream_mode"]).lower()
