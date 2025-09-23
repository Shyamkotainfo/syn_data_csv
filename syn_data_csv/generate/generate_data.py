import pandas as pd
import csv
from tqdm import tqdm
from .generate_text_prompt import generate_prompt
from syn_data_csv.llm.llm_providers import generate_text_from_llm
from syn_data_csv.utils.constants import MAX_BATCH_SIZE, MAX_DEFAULT_ROWS

def _extract_total_rows():
    try:
        rows = int(input("How many rows do you want to generate? "))
        return rows
    except ValueError:
        print("⚠️ Using default row count")
        return MAX_DEFAULT_ROWS

def _get_columns(ref_data):
    column_names = ref_data.columns.tolist()
    expected_columns = len(column_names)
    return column_names, expected_columns

def generate_synthetic_data(ref_data, provider, api_key, model):
    total_rows = _extract_total_rows()
    column_names, expected_columns = _get_columns(ref_data)

    all_data = []
    generated_set = set()
    total_generated_rows = 0

    with tqdm(total=total_rows, desc="Generating synthetic data") as pbar:
        while total_generated_rows < total_rows:
            batch_size = min(MAX_BATCH_SIZE, total_rows - total_generated_rows)

            prompt = generate_prompt(ref_data, batch_size)

            response = generate_text_from_llm(prompt, provider, api_key, model)

            for row in response.strip().split("\n"):
                row_values = next(csv.reader([row], quotechar='"'))

                if len(row_values) != expected_columns:
                    continue

                row_tuple = tuple(row_values)
                if row_tuple not in generated_set:
                    generated_set.add(row_tuple)
                    all_data.append(dict(zip(column_names, row_values)))
                    total_generated_rows += 1
                    pbar.update(1)

                if total_generated_rows >= total_rows:
                    break

    print(f"✅ Total generated rows: {total_generated_rows}")
    return pd.DataFrame(all_data)
