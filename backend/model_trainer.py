import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, classification_report
import pickle
import os

# ── 1. Load Dataset ──────────────────────────────────────────────
COLUMNS = [
    "age", "workclass", "fnlwgt", "education", "education_num",
    "marital_status", "occupation", "relationship", "race", "gender",
    "capital_gain", "capital_loss", "hours_per_week", "native_country", "income"
]

def load_dataset():
    filepath = os.path.join(os.path.dirname(__file__), "adult.csv")
    df = pd.read_csv(filepath, names=COLUMNS, sep=",", skipinitialspace=True)
    return df

# ── 2. Clean Dataset ─────────────────────────────────────────────
def clean_dataset(df):
    # Replace missing values marked as '?'
    df = df.replace("?", np.nan)
    df = df.dropna()

    # Strip whitespace from string columns
    df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)

    # Convert income to binary: >50K = 1, <=50K = 0
    df["income"] = df["income"].apply(lambda x: 1 if ">50K" in x else 0)

    return df

# ── 3. Encode & Prepare Features ─────────────────────────────────
def prepare_features(df):
    df = df.copy()

    # Store sensitive attributes before encoding
    sensitive = df[["gender", "race"]].copy()

    # Drop columns not useful for prediction
    drop_cols = ["fnlwgt", "native_country", "education"]
    df = df.drop(columns=drop_cols)

    # Encode all categorical columns
    label_encoders = {}
    for col in df.select_dtypes(include="object").columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])
        label_encoders[col] = le

    X = df.drop(columns=["income"])
    y = df["income"]

    return X, y, sensitive, label_encoders

# ── 4. Train Model ───────────────────────────────────────────────
def train_model():
    print("Loading dataset...")
    df = load_dataset()

    print("Cleaning dataset...")
    df = clean_dataset(df)

    print(f"Dataset shape after cleaning: {df.shape}")

    print("Preparing features...")
    X, y, sensitive, label_encoders = prepare_features(df)

    # Split into train and test sets
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print("Training Random Forest model...")
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    print(f"\nModel Accuracy: {accuracy:.4f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred))

    # Save model and encoders
    model_path = os.path.join(os.path.dirname(__file__), "model.pkl")
    encoders_path = os.path.join(os.path.dirname(__file__), "label_encoders.pkl")

    with open(model_path, "wb") as f:
        pickle.dump(model, f)

    with open(encoders_path, "wb") as f:
        pickle.dump(label_encoders, f)

    print(f"\nModel saved to model.pkl")
    print(f"Encoders saved to label_encoders.pkl")

    return model, X_test, y_test, sensitive

if __name__ == "__main__":
    train_model()