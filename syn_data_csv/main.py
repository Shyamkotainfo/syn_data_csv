# main.py
import sys
from syn_data_csv.utils.validate_files import validate_csv
from syn_data_csv.llm.llm_setup import get_api_key_model
from syn_data_csv.generate.generate_data import generate_synthetic_data
from syn_data_csv.generate.output import generate_output

def get_csv_data():
    # Get CSV filename from args
    args = sys.argv[1:]
    if not args:
        print("❌ Please provide a CSV reference file as argument.")
        sys.exit(1)

    csv_file = args[0]
    df_ref, delimiter = validate_csv(csv_file)
    input_filename = csv_file

    # Get LLM Provider, API Key, and Model
    provider, api_key, model = get_api_key_model()

    # Generate synthetic data
    df_synthetic = generate_synthetic_data(df_ref, provider, api_key, model)

    # Save synthetic data
    generate_output(df_synthetic, input_filename, delimiter)

if __name__ == "__main__":
    get_csv_data()
