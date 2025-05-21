import pandas as pd
import csv
import logging
from validate import CSVValidator
from generate_text_prompt import PromptGenerator

logging.basicConfig(level=logging.ERROR, filename="error.log", filemode="a", format="%(asctime)s - %(levelname)s - %(message)s")

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

        if self.total_rows > 1000:
            logging.error("Row count exceeds the allowed limit of 1000.")
            raise ValueError("Row count exceeds the allowed limit of 1000.")

    def generate(self):
        """Generate synthetic data in batches with retry logic."""
        reference_samples = CSVValidator.load_reference_data(self.ref_data_path) if self.ref_data_path else None
        total_generated_rows = 0
        all_data = []
        retry_count = 0
        max_retries = 3

        while total_generated_rows < self.total_rows:
            if retry_count > max_retries:
                logging.error("LLM retry limit exceeded (3 retries). Aborting data generation.")
                raise RuntimeError("LLM retry limit exceeded (3 retries). Aborting data generation.")
            
            prompt = PromptGenerator.create_prompt(self.config, reference_samples)

            try:
                response = PromptGenerator.generate_text(prompt, self.client)
                rows = response.strip().split("\n")
            except Exception as e:
                logging.error(f"LLM request failed: {e}")
                retry_count += 1
                continue

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
