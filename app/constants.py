import os
from dotenv import load_dotenv


load_dotenv() 

DEFAULT_API_KEY = os.getenv("API_KEY")
DEFAULT_MODEL = os.getenv("MODEL", "mistral-saba-24b")