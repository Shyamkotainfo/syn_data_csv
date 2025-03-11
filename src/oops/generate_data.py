import pandas as pd
import csv
from validate import CSVValidator
from generate_text_prompt import PromptGenerator


class DataGenerator:
    """Generates synthetic data using LLM."""

    def __init__(self, config, ref_data_path, client):
        self.config = config
        self.ref_data_path = ref_data_path
        self.client = client
        self.total_rows = int(config.get("row_count", [100])[0])
        self.column_names = [col["name"] for col in config.get("columns", [])]
        self.expected_columns = len(self.column_names)
        self.generated_set = set()

    def generate(self):
        """Generate synthetic data in batches."""
        reference_samples = CSVValidator.load_reference_data(self.ref_data_path) if self.ref_data_path else None
        max_rows_per_batch = 50
        total_generated_rows = 0
        all_data = []

        while total_generated_rows < self.total_rows:
            remaining_rows = self.total_rows - total_generated_rows
            batch_size = min(max_rows_per_batch, remaining_rows)
            prompt = PromptGenerator.create_prompt(self.config, reference_samples)
            response = PromptGenerator.generate_text(prompt, self.client)

            rows = response.strip().split("\n")
            for row in rows:
                row_values = next(csv.reader([row], quotechar='"'))
                if len(row_values) != self.expected_columns:
                    continue
                row_tuple = tuple(row_values)
                if row_tuple not in self.generated_set:
                    self.generated_set.add(row_tuple)
                    all_data.append(dict(zip(self.column_names, row_values)))
                    total_generated_rows += 1
                if total_generated_rows >= self.total_rows:
                    break

        print("Total Generated Rows:", total_generated_rows)
        return pd.DataFrame(all_data)
