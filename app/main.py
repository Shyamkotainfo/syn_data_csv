import pandas as pd
import sys
from groq import Groq # Import Groq API

from syn_data_gen.app.validate import load_yaml, validate_yaml, validate_csv
from syn_data_gen.app.generate_data import generate_synthetic_data

# Initialize Groq client
client = Groq(api_key="")  # Replace with your API key
generated_set = set()  # Track unique rows


def main():

    # import from constansts.py
    api_key = DEFAULT_API_KEY
    model = DEFAULT_MODEL

    args = sys.argv[1:]

    

    # Generate synthetic data
    df = generate_synthetic_data(config, reference_file, client)
    
    if not df.empty:
        df.to_csv("synthetic_data.csv", index=False)
        print("✅ Synthetic data saved to synthetic_data.csv")
    else:
        print("❌ No valid data to save.")

if __name__ == "__main__":
    main()
