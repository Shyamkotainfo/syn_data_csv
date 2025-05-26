import sys

from app.validate_files import process_and_validate_files
from app.ai_acceleratos import get_api_key_model
# from app.generate_data import generate_synthetic_data
# from app.output import generate_ouput


def main():

    # Process and validate files
    args = sys.argv[1:]
    config, reference_file = process_and_validate_files(args)

    # Get API Key and Model
    api_key, model = get_api_key_model()
    
    # Generate synthetic data
    df = generate_synthetic_data(config, reference_file, api_key, model)
    
    # Save Synthetic data
    generate_ouput(df)

if __name__ == "__main__":
    main()
