import os

def generate_output(df, input_filename, delimiter=','):
    if not df.empty:
        base_name = os.path.splitext(os.path.basename(input_filename))[0]
        output_file = f"{base_name}_synthetic.csv"
        df.to_csv(output_file, index=False, sep=delimiter)
        print(f"✅ Synthetic data saved to {output_file} with delimiter '{delimiter}'")
    else:
        print("❌ No valid data to save.")