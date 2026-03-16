import pandas as pd
import numpy as np
import random
import os
import math
import statistics

random.seed(42)
np.random.seed(42)

EMPLOYMENT_TYPES = ["full_time", "part_time", "freelancer", "gig_worker", "seasonal"]
INTEREST_RATES = {
    "full_time": 0.07, "part_time": 0.10,
    "freelancer": 0.13, "gig_worker": 0.15, "seasonal": 0.14
}

def generate_monthly_incomes(employment_type, n_months):
    profiles = {
        "full_time":  {"mean": 5000, "std": 300,  "zero_prob": 0.0},
        "part_time":  {"mean": 2500, "std": 600,  "zero_prob": 0.05},
        "freelancer": {"mean": 3500, "std": 1800, "zero_prob": 0.10},
        "gig_worker": {"mean": 2800, "std": 1500, "zero_prob": 0.15},
        "seasonal":   {"mean": 3000, "std": 2000, "zero_prob": 0.20},
    }
    p = profiles.get(employment_type, profiles["freelancer"])
    incomes = []
    for _ in range(n_months):
        if random.random() < p["zero_prob"]:
            incomes.append(random.uniform(200, 800))
        else:
            incomes.append(max(300, np.random.normal(p["mean"], p["std"])))
    return incomes

def calculate_features(incomes, loan_amount, loan_term_months, employment_type):
    avg = sum(incomes) / len(incomes)
    std_dev = statistics.stdev(incomes) if len(incomes) > 1 else 0
    cv = (std_dev / avg * 100) if avg > 0 else 100
    stability_score = max(0, min(100, 100 - cv))

    rate = INTEREST_RATES.get(employment_type, 0.15)
    r = rate / 12
    n = loan_term_months
    monthly_payment = loan_amount * (r * math.pow(1+r, n)) / (math.pow(1+r, n) - 1)
    dti = (monthly_payment / avg * 100) if avg > 0 else 100

    emp_enc = {"full_time": 4, "part_time": 3, "freelancer": 2, "gig_worker": 1, "seasonal": 1}
    emp_code = emp_enc.get(employment_type, 1)

    # ── Anomaly feature ──────────────────────────────────────────
    # High stability for unstable employment = suspicious
    # Real freelancers/gig workers NEVER have perfectly stable income
    high_risk_emp = emp_code <= 2
    stability_anomaly = 1 if (high_risk_emp and stability_score >= 88) else 0

    return {
        "stability_score": round(stability_score, 2),
        "average_monthly_income": round(avg, 2),
        "income_variance": round(std_dev ** 2, 2),
        "debt_to_income_ratio": round(min(dti, 150), 2),
        "min_income": round(min(incomes), 2),
        "max_income": round(max(incomes), 2),
        "loan_amount": loan_amount,
        "loan_term_months": loan_term_months,
        "employment_type_encoded": emp_code,
        "months_of_data": len(incomes),
        "loan_to_income_ratio": round(loan_amount / (avg * 12), 2) if avg > 0 else 10,
        "stability_anomaly": stability_anomaly   # 🚨 NEW FEATURE
    }

def determine_label(features):
    stability = features["stability_score"]
    dti = features["debt_to_income_ratio"]
    avg_income = features["average_monthly_income"]
    lti = features["loan_to_income_ratio"]
    min_income = features["min_income"]
    anomaly = features["stability_anomaly"]

    # ── Hard denial: suspicious stability ────────────────────────
    if anomaly == 1 and stability >= 95:
        return 0  # denied — too suspicious

    if anomaly == 1 and stability >= 88:
        return 1  # review — suspicious but not definitive

    # Hard denials
    if dti > 70: return 0
    if stability < 20: return 0
    if avg_income < 1000: return 0
    if min_income < 300 and stability < 40: return 0
    if lti > 5: return 0

    # Hard approvals
    if stability >= 75 and dti <= 25 and lti <= 1.5 and anomaly == 0:
        return 2

    # Scoring
    score = 0
    if stability >= 70: score += 40
    elif stability >= 60: score += 30
    elif stability >= 50: score += 20
    elif stability >= 40: score += 10

    if dti <= 25: score += 35
    elif dti <= 35: score += 25
    elif dti <= 45: score += 15
    elif dti <= 55: score += 5

    if avg_income >= 5000: score += 15
    elif avg_income >= 3500: score += 10
    elif avg_income >= 2000: score += 5

    if lti <= 1: score += 10
    elif lti <= 2: score += 7
    elif lti <= 3: score += 3

    score += np.random.normal(0, 4)

    if score >= 65: return 2
    elif score >= 40: return 1
    else: return 0

def generate_dataset(n_samples=3000):
    records = []
    for _ in range(n_samples):
        employment_type = random.choice(EMPLOYMENT_TYPES)
        n_months = random.randint(3, 12)

        if employment_type == "full_time":
            loan_amount = random.randint(5000, 80000)
        elif employment_type in ["freelancer", "part_time"]:
            loan_amount = random.randint(3000, 40000)
        else:
            loan_amount = random.randint(2000, 25000)

        loan_term_months = random.choice([12, 24, 36, 48, 60])
        incomes = generate_monthly_incomes(employment_type, n_months)
        features = calculate_features(incomes, loan_amount, loan_term_months, employment_type)
        label = determine_label(features)
        features["outcome"] = label
        records.append(features)

    df = pd.DataFrame(records)
    print(f"✅ Generated {len(df)} samples")
    print(f"\nLabel distribution:")
    counts = df['outcome'].value_counts().sort_index()
    labels = {0: "Denied", 1: "Review", 2: "Approved"}
    for k, v in counts.items():
        print(f"  {labels[k]}: {v} ({v/len(df)*100:.1f}%)")

    suspicious = df[df["stability_anomaly"] == 1]
    print(f"\n🚨 Suspicious applications flagged: {len(suspicious)}")
    return df

if __name__ == "__main__":
    df = generate_dataset(3000)
    output_path = os.path.join(os.path.dirname(__file__), "training_data.csv")
    df.to_csv(output_path, index=False)
    print(f"\n✅ Saved to {output_path}")
