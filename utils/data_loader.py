import os
import pandas as pd

def load_data():
    """
    Load and preprocess the mental health dataset.
    Returns a cleaned pandas DataFrame.
    """

    # Use relative path to make it work on all platforms
    csv_path = os.path.join(os.path.dirname(__file__), "..", "data", "mental_health_cleaned.csv")

    # Check if the file exists before reading
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found at: {csv_path}")

    # Load dataset
    df = pd.read_csv(csv_path)  

    # Convert column names to lowercase and replace spaces with underscores
    df.columns = df.columns.str.lower().str.replace(" ", "_")

    # Drop duplicate rows (if any)
    df = df.drop_duplicates()

    # Convert categorical columns to category type for efficiency
    categorical_columns = ["gender", "country", "occupation", "treatment"]
    for col in categorical_columns:
        if col in df.columns:
            df[col] = df[col].astype("category")

    return df
