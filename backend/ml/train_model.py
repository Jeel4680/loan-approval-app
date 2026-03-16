import pandas as pd
import numpy as np
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

print("=" * 50)
print("LOAN APPROVAL ML MODEL TRAINING")
print("=" * 50)

data_path = os.path.join(os.path.dirname(__file__), "training_data.csv")
df = pd.read_csv(data_path)
print(f"\n✅ Loaded {len(df)} training samples")

FEATURE_COLUMNS = [
    "stability_score",
    "average_monthly_income",
    "income_variance",
    "debt_to_income_ratio",
    "min_income",
    "max_income",
    "loan_amount",
    "loan_term_months",
    "employment_type_encoded",
    "months_of_data",
    "loan_to_income_ratio",
    "stability_anomaly"        # 🚨 NEW
]

X = df[FEATURE_COLUMNS]
y = df["outcome"]

print(f"\n📊 Label distribution:")
counts = y.value_counts().sort_index()
labels = {0: "Denied", 1: "Review", 2: "Approved"}
for k, v in counts.items():
    print(f"  {labels[k]}: {v} ({v/len(y)*100:.1f}%)")

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("\nMODEL 1: LOGISTIC REGRESSION")
lr_model = LogisticRegression(max_iter=1000, random_state=42, class_weight='balanced')
lr_model.fit(X_train_scaled, y_train)
lr_pred = lr_model.predict(X_test_scaled)
lr_acc = accuracy_score(y_test, lr_pred)
print(f"Accuracy: {lr_acc*100:.2f}%")
print(classification_report(y_test, lr_pred, target_names=["Denied","Review","Approved"]))

print("\nMODEL 2: RANDOM FOREST")
rf_model = RandomForestClassifier(
    n_estimators=200, max_depth=12,
    min_samples_leaf=5, class_weight='balanced', random_state=42
)
rf_model.fit(X_train, y_train)
rf_pred = rf_model.predict(X_test)
rf_acc = accuracy_score(y_test, rf_pred)
print(f"Accuracy: {rf_acc*100:.2f}%")
print(classification_report(y_test, rf_pred, target_names=["Denied","Review","Approved"]))

print("\n📊 Feature Importance:")
for feat, imp in sorted(zip(FEATURE_COLUMNS, rf_model.feature_importances_), key=lambda x: x[1], reverse=True):
    bar = "█" * int(imp * 50)
    print(f"  {feat:<35} {bar} {imp:.4f}")

best_model = rf_model if rf_acc >= lr_acc else lr_model
best_name = "Random Forest" if rf_acc >= lr_acc else "Logistic Regression"
print(f"\n🏆 Best: {best_name} ({max(rf_acc,lr_acc)*100:.2f}%)")

model_dir = os.path.dirname(__file__)
joblib.dump(best_model, os.path.join(model_dir, "loan_model.pkl"))
joblib.dump(scaler, os.path.join(model_dir, "scaler.pkl"))
joblib.dump(FEATURE_COLUMNS, os.path.join(model_dir, "feature_columns.pkl"))
print("✅ Model saved!")
