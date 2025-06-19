def generate_output(df, delimiter=','):

    if not df.empty:
        df.to_csv("synthetic_data_new.csv", index=False, sep=delimiter)
        print(f"✅ Synthetic data saved to synthetic_data_new.csv with delimiter '{delimiter}'")
    else:
        print("❌ No valid data to save.")
