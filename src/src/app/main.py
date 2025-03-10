import pandas as pd
import sys
from groq import Groq # Import Groq API

from validate import load_yaml, validate_yaml, validate_csv
from generate_data import generate_synthetic_data

# Initialize Groq client
client = Groq(api_key="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")  # Replace with your API key
generated_set = set()  # Track unique rows


def main():

    if len(sys.argv) < 3:
        print("❌ Usage: python test1.py config.yaml test_data.csv")
        sys.exit(1)

    yaml_file = sys.argv[1]
    reference_file = sys.argv[2]

    # Load YAML configuration
    config = load_yaml(yaml_file)

    # Validate YAML format
    try:
        validate_yaml(config)
    except ValueError as e:
        print(f"❌ YAML validation error: {e}")
        sys.exit(1)

    # Validate CSV format
    expected_columns = [col["name"] for col in config["columns"]]
    try:
        validate_csv(reference_file, expected_columns)
    except ValueError as e:
        print(f"❌ CSV validation error: {e}")
        sys.exit(1)

    # Generate synthetic data
    df = generate_synthetic_data(config, reference_file, client)
    
    if not df.empty:
        df.to_csv("synthetic_data.csv", index=False)
        print("✅ Synthetic data saved to synthetic_data.csv")
    else:
        print("❌ No valid data to save.")

if __name__ == "__main__":
    main()
