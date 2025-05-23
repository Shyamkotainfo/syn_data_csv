import yaml
import pandas as pd
import json
import sys
import csv
from groq import Groq  # Import Groq API

# Initialize Groq client
client = Groq(api_key="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")  # Replace with your API key

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

def validate_yaml(config):
    """Validate the structure of the YAML configuration file."""
    required_keys = {"columns", "prompt"}
    
    if not isinstance(config, dict):
        raise ValueError("YAML configuration should be a dictionary.")

    missing_keys = required_keys - config.keys()
    if missing_keys:
        raise ValueError(f"Missing required keys in YAML: {missing_keys}")

    if not isinstance(config["columns"], list) or not all(isinstance(col, dict) for col in config["columns"]):
        raise ValueError("Invalid format for 'columns' in YAML. It should be a list of dictionaries.")

    for col in config["columns"]:
        if "name" not in col or "type" not in col:
            raise ValueError(f"Each column must have 'name' and 'type' fields. Found: {col}")

    print("✅ YAML configuration format is valid.")

def validate_csv(file_path, expected_columns):
    """Validate the CSV reference file format without enforcing column order."""
    try:
        df = pd.read_csv(file_path, nrows=5)  # Read only the first few rows
    except Exception as e:
        raise ValueError(f"Error reading CSV file: {e}")

    actual_columns = set(df.columns)
    expected_columns_set = set(expected_columns)

    missing_columns = expected_columns_set - actual_columns
    extra_columns = actual_columns - expected_columns_set

    if missing_columns:
        raise ValueError(f"CSV is missing expected columns: {missing_columns}")

    print("✅ CSV reference file format is valid.")

def generate_text(prompt):

    """Generate text using Groq's Mixtral model."""
    messages = [{"role": "user", "content": prompt}]
    
    # Call Groq API for text generation
    completion = client.chat.completions.create(
        model="mixtral-8x7b-32768",
        messages=messages,
        temperature=1,
        max_tokens=6000,
        top_p=1,
        stream=True
    )

    # Capture streamed output
    response_text = ""
    for chunk in completion:
        if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
            response_text += chunk.choices[0].delta.content

    return response_text.strip()

def generate_prompt(config, reference_samples):
    """Construct the LLM prompt dynamically."""
    num_rows = config.get("num_rows", 100)
    user_prompt = config.get("prompt", [""])[0]  # Extract user-given text
    column_definitions = "\n".join(
        [f"- {col['name']} ({col['type']})" for col in config.get('columns', [])]
    )

    prompt = f"""
    Generate {num_rows} unique rows of synthetic data in CSV format with these columns:
    {column_definitions}

    **Rules:**

    - Data format: CSV only.
    - Rows must be unique; columns need not be unique.
    - Include at least one primary key.
    - Ensure the data follows a realistic pattern.
    - Strings shouldn't be in quotes. Ex: ('""user101"" -->incorrect, user101  --> correct)
    - **Replicate the pattern in reference data**
    - Take count of rows form the user instruction.
    - **Each row must contain exactly {len(config.get("columns", []))} values. No missing or extra fields.**
    - **Output format: Only comma-separated values (NO HEADER, NO EXTRA TEXT).**'
    - **Ensure CSV output has NO extra text, NO headers, NO extra spacing, and is STRICTLY comma-separated.**
    - **No excessive quotation marks unless necessary for escaping commas in text fields.**



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
    """Generate synthetic data in batches while ensuring valid CSV format."""

    # Extract total rows from YAML config
    total_rows = int(config.get("row_count", [100])[0])  # Ensure it's a single value
    
    column_names = [col["name"] for col in config.get("columns", [])]
    expected_columns = len(column_names)
    
    # Load reference data if provided
    reference_samples = load_reference_data(ref_data_path) if ref_data_path else None

    max_rows_per_batch = 50  # Limit per batch
    total_generated_rows = 0
    generated_set = set()
    all_data = []

    while total_generated_rows < total_rows:  
        remaining_rows = total_rows - total_generated_rows
        batch_size = min(max_rows_per_batch, remaining_rows)

        # Adjust prompt dynamically for each batch
        prompt = generate_prompt(config, reference_samples)

        response = generate_text(prompt)
        print(f"Batch Response ({total_generated_rows + 1}-{total_generated_rows + batch_size}):", response)

        rows = response.strip().split("\n")

        for row in rows:
            row_values = next(csv.reader([row], quotechar='"'))  # Proper CSV parsing

            if len(row_values) != expected_columns:
                continue  # Skip invalid rows

            row_tuple = tuple(row_values)
            if row_tuple not in generated_set:
                generated_set.add(row_tuple)
                all_data.append(dict(zip(column_names, row_values)))
                total_generated_rows += 1

            if total_generated_rows >= total_rows:  # Stop when we reach required total rows
                break

    print("Total Generated Rows:", total_generated_rows)
    return pd.DataFrame(all_data)


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
    df = generate_synthetic_data(config, reference_file)
    
    if not df.empty:
        df.to_csv("synthetic_data.csv", index=False)
        print("✅ Synthetic data saved to synthetic_data.csv")
    else:
        print("❌ No valid data to save.")

if __name__ == "__main__":
    main()
