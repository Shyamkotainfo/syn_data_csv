import pandas as pd
import sys
from groq import Groq  # Import Groq API

from validate import YAMLValidator, CSVValidator
from generate_data import DataGenerator
from ouput import OutputHandler

class SyntheticDataPipeline:
    """Manages the entire synthetic data generation process."""

    def __init__(self, yaml_file, reference_file, api_key):
        self.yaml_file = yaml_file
        self.reference_file = reference_file
        self.client = Groq(api_key=api_key)  # Initialize Groq client

    def run(self):
        """Execute the synthetic data generation pipeline."""
        # Load and validate YAML
        config = YAMLValidator.load_yaml(self.yaml_file)
        try:
            YAMLValidator.validate_yaml(config)
        except ValueError as e:
            print(f"❌ YAML validation error: {e}")
            sys.exit(1)

        # Validate CSV format
        expected_columns = [col["name"] for col in config["columns"]]
        try:
            CSVValidator.validate_csv(self.reference_file, expected_columns)
        except ValueError as e:
            print(f"❌ CSV validation error: {e}")
            sys.exit(1)

        # Generate synthetic data
        generator = DataGenerator(config, self.reference_file, self.client)
        df = generator.generate()

        OutputHandler.save_to_csv(df)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("❌ Usage: python main.py config.yaml test_data.csv")
        sys.exit(1)
    pipeline = SyntheticDataPipeline(sys.argv[1], sys.argv[2], api_key="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")
    pipeline.run()
