import pandas as pd


class OutputHandler:
    """Handles output saving and logging."""

    @staticmethod
    def save_to_csv(df, filename="synthetic_data.csv"):
        if not df.empty:
            df.to_csv(filename, index=False)
            print(f"✅ Synthetic data saved to {filename}")
        else:
            print("❌ No valid data to save.")
