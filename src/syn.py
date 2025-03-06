import yaml
import pandas as pd
import json
import sys
import csv
from huggingface_hub import InferenceClient

generated_set = set()  # Track unique rows

def load_yaml(file_path):
    """Load YAML configuration file."""
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def load_reference_data(ref_data_path):
    """Load reference CSV file if provided."""
    try:
        df = pd.read_csv(ref_data_path)
        return df.head(5).to_dict(orient="records")  # Extract sample structure
    except Exception as e:
        print(f"⚠️ Warning: Could not load reference data: {e}")
        return None

def generate_text(prompt):
    """Generate text using Hugging Face API."""
    client = InferenceClient(api_key="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")  # Replace with your API key
    messages = [{"role": "user", "content": prompt}]
    completion = client.chat.completions.create(  # Corrected method call
        model="mistralai/Mistral-7B-Instruct-v0.3",
        messages=messages, 
        max_tokens=1000,
    )
    return completion.choices[0].message.content.strip()

def generate_prompt(config, reference_samples):
    """Construct the LLM prompt dynamically."""
    num_rows = config.get("num_rows", 100)
    user_prompt = config.get("prompt", [""])[0]  # Extract user-given text
    column_definitions = "\n".join(
        [f"- {col['name']} ({col['type']})" for col in config.get('columns', [])]
    )

    prompt = f"""
    Generate {num_rows} unique rows of synthetic e-commerce transaction data in CSV format with these columns:
    {column_definitions}
    
    **Rules:**
    - Data should be only csv
    - Ensure the output follows a realistic pattern.
    - Output format: Only comma-separated values (NO HEADER, NO EXTRA TEXT).

    ----
    - User instruction: {user_prompt}
    """
    
    if reference_samples:
        prompt += f"""
        **Reference Data Examples:**
        {json.dumps(reference_samples, indent=4)}

        - Ensure the generated data follows this structure.
        """
    
    return prompt.strip()

def generate_synthetic_data(config, ref_data_path):
    """Generate synthetic data ensuring valid CSV format."""
    column_names = [col["name"] for col in config.get("columns", [])]
    expected_columns = len(column_names)

    # Load reference data if provided
    reference_samples = load_reference_data(ref_data_path) if ref_data_path else None

    prompt = generate_prompt(config, reference_samples)
    response = generate_text(prompt)
    rows = response.strip().split("\n")

    generated_set = set()  # Ensure unique rows
    all_data = []

    for row in rows:
        # Use csv.reader to properly parse quoted fields
        row_values = next(csv.reader([row]))  # Parses a single row correctly

        if len(row_values) != expected_columns:
            print(f"⚠️ Skipping invalid row (Expected {expected_columns} values, got {len(row_values)}): {row}")
            continue

        # Handle JSON fields correctly (e.g., DeviceInfo)
        for idx, col in enumerate(config.get("columns", [])):
            if col["type"] == "dict":
                try:
                    row_values[idx] = json.loads(row_values[idx])  # Convert to dict
                except json.JSONDecodeError:
                    print(f"⚠️ Warning: Invalid JSON in 'DeviceInfo': {row_values[idx]}")
                    continue  # Skip this row

        row_tuple = tuple(row_values)
        if row_tuple not in generated_set:
            generated_set.add(row_tuple)
            all_data.append(dict(zip(column_names, row_values)))

    if not all_data:
        print("❌ No valid rows generated. Please check the model response.")

    return pd.DataFrame(all_data)

def main():
    if len(sys.argv) < 3:
        print("❌ Usage: python test1.py config.yaml test_data.csv")
        sys.exit(1)

    yaml_file = sys.argv[1]
    reference_file = sys.argv[2]

    config = load_yaml(yaml_file)
    df = generate_synthetic_data(config, reference_file)
    
    if not df.empty:
        df.to_csv("synthetic_data.csv", index=False)
        print("✅ Synthetic data saved to synthetic_data.csv")
    else:
        print("❌ No valid data to save.")

if __name__ == "__main__":
    main()
