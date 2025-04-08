import yaml
import pandas as pd


class YAMLValidator:
    """Handles YAML file loading and validation."""

    @staticmethod
    def load_yaml(file_path):
        try:
            with open(file_path, 'r') as file:
                return yaml.safe_load(file)
        except Exception as e:
            raise ValueError(f"Error loading YAML file: {e}")

    @staticmethod
    def validate_yaml(config):
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


class CSVValidator:
    """Handles CSV file validation."""

    @staticmethod
    def load_reference_data(ref_data_path):
        try:
            df = pd.read_csv(ref_data_path)
            return df.head(5).to_dict(orient="records")
        except Exception as e:
            print(f"⚠️ Warning: Could not load CSV data: {e}")
            return None

    @staticmethod
    def validate_csv(file_path, expected_columns):
        try:
            df = pd.read_csv(file_path, nrows=5)
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {e}")

        actual_columns = set(df.columns)
        expected_columns_set = set(expected_columns)

        missing_columns = expected_columns_set - actual_columns
        extra_columns = actual_columns - expected_columns_set

        if missing_columns:
            raise ValueError(f"CSV is missing expected columns: {missing_columns}")
        
        if extra_columns:
            raise ValueError(f"CSV contains extra columns: {extra_columns}")

        print("✅ CSV reference file format is valid.")
