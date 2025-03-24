import pandas as pd

def load_data():
    """
    Load and preprocess the mental health dataset.
    Returns a cleaned pandas DataFrame.
    """
    # Load dataset
    df = pd.read_csv("E:\CAI 2.0\Programming for AI\libraries\mental_health_dasboard\data\mental_health_cleaned.csv")  

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
