import pandas as pd
import numpy as np
import pickle
import os
from model_trainer import load_dataset, clean_dataset, prepare_features

# ── 1. Load Model ────────────────────────────────────────────────
def load_model():
    model_path = os.path.join(os.path.dirname(__file__), "model.pkl")
    with open(model_path, "rb") as f:
        model = pickle.load(f)
    return model

# ── 2. Compute Bias Metrics ──────────────────────────────────────
def compute_bias_metrics(df, predictions, sensitive_col):
    results = {}
    groups = df[sensitive_col].unique()

    for group in groups:
        mask = df[sensitive_col] == group
        group_preds = predictions[mask]
        positive_rate = group_preds.mean()
        results[group] = round(float(positive_rate), 4)

    return results

# ── 3. Disparate Impact ──────────────────────────────────────────
def disparate_impact(group_rates):
    rates = list(group_rates.values())
    if max(rates) == 0:
        return 0.0
    return round(min(rates) / max(rates), 4)

# ── 4. Statistical Parity ────────────────────────────────────────
def statistical_parity(group_rates):
    rates = list(group_rates.values())
    return round(max(rates) - min(rates), 4)

# ── 5. Equal Opportunity ─────────────────────────────────────────
def equal_opportunity(df, predictions, labels, sensitive_col):
    groups = df[sensitive_col].unique()
    tpr_by_group = {}

    for group in groups:
        mask = (df[sensitive_col] == group) & (labels == 1)
        if mask.sum() == 0:
            tpr_by_group[group] = 0.0
            continue
        tpr = predictions[mask].mean()
        tpr_by_group[group] = round(float(tpr), 4)

    tpr_values = list(tpr_by_group.values())
    diff = round(max(tpr_values) - min(tpr_values), 4)
    return diff, tpr_by_group

# ── 6. Bias Level Rating ─────────────────────────────────────────
def get_bias_level(disparate_impact_score, stat_parity_score):
    if disparate_impact_score >= 0.8 and stat_parity_score <= 0.1:
        return "Low"
    elif disparate_impact_score >= 0.6 and stat_parity_score <= 0.2:
        return "Medium"
    else:
        return "High"

# ── 7. Recommendations ───────────────────────────────────────────
def get_recommendations(bias_level, sensitive_col):
    base = f"Bias detected in '{sensitive_col}' attribute. "
    if bias_level == "Low":
        return base + "Bias is within acceptable range. Continue monitoring regularly."
    elif bias_level == "Medium":
        return base + (
            "Consider reweighing the dataset to balance outcome rates across groups. "
            "Review feature importance to check for proxy discrimination."
        )
    else:
        return base + (
            "High bias detected. Recommend: (1) Reweigh training data, "
            "(2) Apply adversarial debiasing, "
            "(3) Remove or mask the sensitive attribute and its proxies, "
            "(4) Consult a fairness expert before deploying this model."
        )

# ── 8. Full Bias Report ──────────────────────────────────────────
def run_bias_analysis(sensitive_col="gender"):
    print(f"\nRunning bias analysis on: {sensitive_col}")

    # Load and prepare data
    df = load_dataset()
    df = clean_dataset(df)
    X, y, sensitive, _ = prepare_features(df)

    # Load model and predict
    model = load_model()
    predictions = model.predict(X)

    # Attach sensitive column back for analysis
    sensitive_raw = df[sensitive_col].values[:len(predictions)]
    sensitive_series = pd.Series(sensitive_raw, name=sensitive_col)
    labels = y.values[:len(predictions)]

    # Compute metrics
    group_rates = compute_bias_metrics(
        pd.DataFrame({sensitive_col: sensitive_series}),
        predictions,
        sensitive_col
    )

    di_score = disparate_impact(group_rates)
    sp_score = statistical_parity(group_rates)
    eo_score, tpr_by_group = equal_opportunity(
        pd.DataFrame({sensitive_col: sensitive_series}),
        predictions,
        labels,
        sensitive_col
    )

    bias_level = get_bias_level(di_score, sp_score)
    recommendations = get_recommendations(bias_level, sensitive_col)

    # Build report
    report = {
        "sensitive_attribute": sensitive_col,
        "group_positive_rates": group_rates,
        "disparate_impact_score": di_score,
        "statistical_parity_score": sp_score,
        "equal_opportunity_score": eo_score,
        "tpr_by_group": tpr_by_group,
        "overall_bias_level": bias_level,
        "recommendations": recommendations
    }

    # Print summary
    print(f"\n{'='*50}")
    print(f"  BIAS ANALYSIS REPORT — {sensitive_col.upper()}")
    print(f"{'='*50}")
    print(f"  Group Positive Rates : {group_rates}")
    print(f"  Disparate Impact     : {di_score}  (>=0.8 is fair)")
    print(f"  Statistical Parity   : {sp_score}  (<=0.1 is fair)")
    print(f"  Equal Opportunity    : {eo_score}  (<=0.1 is fair)")
    print(f"  Bias Level           : {bias_level}")
    print(f"  Recommendations      : {recommendations}")
    print(f"{'='*50}\n")

    return report

if __name__ == "__main__":
    # Test on gender
    run_bias_analysis("gender")
    # Test on race
    run_bias_analysis("race")