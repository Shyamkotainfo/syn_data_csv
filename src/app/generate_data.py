import pandas as pd
import csv

from validate import load_reference_data
from generate_text_prompt import generate_prompt, generate_text



def generate_synthetic_data(config, ref_data_path, client):
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

        response = generate_text(prompt, client)
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