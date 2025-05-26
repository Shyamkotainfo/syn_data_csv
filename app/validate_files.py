import yaml
import pandas as pd


def load_yaml(file_path):
    """Load YAML configuration file."""
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)


def load_reference_data(ref_data_path):
    """Load reference CSV file if provided."""
    try:
        df = pd.read_csv(ref_data_path)
        return df.head(5).to_dict(orient="records")  
    except Exception as e:
        print(f"⚠️ Warning: Could not load csv data: {e}")
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
    
    if extra_columns:
        raise ValueError(f"CSV is getting more columns: {extra_columns}")

    print("✅ CSV reference file format is valid.")


yaml_file = None
reference_file = None

# Handle case where last two args are API key and model
    if len(args) >= 2 and not args[-2].endswith(('.yaml', '.yml', '.csv')):
        api_key = args[-2]
        model = args[-1]
        file_args = args[:-2]
    elif len(args) >= 1 and not args[-1].endswith(('.yaml', '.yml', '.csv')):
        api_key = args[-1]
        file_args = args[:-1]
    else:
        file_args = args

    # Identify YAML and CSV files
    for arg in file_args:
        if arg.endswith(('.yaml', '.yml')):
            yaml_file = arg
        elif arg.endswith('.csv'):
            reference_file = arg

    if not yaml_file and not reference_file:
        print("❌ No valid .yaml or .csv files provided.")
        print("✅ Usage: python test1.py <file.yaml> <file.csv> [api_key] [model]")
        sys.exit(1)

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