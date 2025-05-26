from groq import Groq # Import Groq API

# import from constansts.py
    api_key = DEFAULT_API_KEY
    model = DEFAULT_MODEL
# Initialize Groq client
client = Groq(api_key="")  # Replace with your API key
generated_set = set()  # Track unique rows
