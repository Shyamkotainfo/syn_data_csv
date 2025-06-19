import yaml
import os

# Get the absolute path to the config.yaml file in the same directory
CONFIG_PATH = os.path.join(os.path.dirname(__file__), 'config.yaml')

# Read the YAML file
with open(CONFIG_PATH, 'r') as f:
    config = yaml.safe_load(f)

# Access keys safely
GROQ_API_KEY = config.get("GROQ_API")
HF_API_KEY = config.get("HF_API")


DEFAULTS = {
    "groq": {
        "api_key": GROQ_API_KEY,
        "model": "llama3-70b-8192"
    },
    "huggingface": {
        "api_key": HF_API_KEY,
        "model": "mistralai/Mixtral-8x7B-Instruct-v0.1"
    }
}

SUPPORTED_PROVIDERS = ["groq", "huggingface"]

MAX_BATCH_SIZE = 100
MAX_DEFAULT_ROWS = 100