import shap
import pickle
import numpy as np
import pandas as pd
import os
from model_trainer import load_dataset, clean_dataset, prepare_features

def load_model():
    model_path = os.path.join(os.path.dirname(__file__), "model.pkl")
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    return model

def get_shap_explanation(sample_size=100):
    print("Loading data and model...")
    df = load_dataset()
    df = clean_dataset(df)
    X, y, sensitive, _ = prepare_features(df)

    model = load_model()
    X_sample = X.iloc[:sample_size]

    print("Computing SHAP values (this may take a moment)...")
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_sample)

    if isinstance(shap_values, list):
        shap_vals = shap_values[1]
    else:
        shap_vals = shap_values

    if shap_vals.ndim == 3:
        shap_vals = shap_vals[:, :, 1]

    mean_abs_shap = np.abs(shap_vals).mean(axis=0)
    feature_importance = pd.DataFrame({
        "feature": X.columns.tolist(),
        "importance": mean_abs_shap.tolist()
    }).sort_values("importance", ascending=False)

    print("\n--- Global Feature Importance (SHAP) ---")
    print(feature_importance.to_string(index=False))

    feature_names = X.columns.tolist()
    gender_impact = None
    race_impact = None

    if "gender" in feature_names:
        gender_idx = feature_names.index("gender")
        gender_impact = round(float(np.abs(shap_vals[:, gender_idx]).mean()), 4)
        print(f"\nGender SHAP Impact : {gender_impact}")

    if "race" in feature_names:
        race_idx = feature_names.index("race")
        race_impact = round(float(np.abs(shap_vals[:, race_idx]).mean()), 4)
        print(f"Race SHAP Impact   : {race_impact}")

    def explain_single(index=0):
        sample = X_sample.iloc[[index]]
        sv = shap_vals[index]
        explanation = []
        for fname, fval, sval in zip(feature_names, sample.values[0], sv):
            explanation.append({
                "feature": fname,
                "value": round(float(fval), 4),
                "shap_value": round(float(sval), 4),
                "direction": "increases bias" if sval > 0 else "decreases bias"
            })
        explanation = sorted(explanation, key=lambda x: abs(x["shap_value"]), reverse=True)
        return explanation[:5]

    top_factors = explain_single(0)
    print("\n--- Top 5 Factors for Sample #0 ---")
    for f in top_factors:
        print(f"  {f['feature']:20s} | value: {f['value']:8.4f} | shap: {f['shap_value']:8.4f} | {f['direction']}")

    result = {
        "feature_importance": feature_importance.to_dict(orient="records"),
        "gender_shap_impact": gender_impact,
        "race_shap_impact": race_impact,
        "sample_explanation": top_factors
    }

    return result

if __name__ == "__main__":
    get_shap_explanation(sample_size=100)