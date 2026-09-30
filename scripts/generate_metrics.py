import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix

# 1. Load 500-sample benchmark results
csv_path = os.path.join("results", "large_evaluation_benchmark_500.csv")
if not os.path.exists(csv_path):
    print(f"[ERROR] Benchmark results not found at {csv_path}")
    exit(1)

df = pd.read_csv(csv_path)

# Normalize labels
y_true = df["ground_truth"].str.strip().str.lower()
y_pred = df["predicted"].str.strip().str.lower()

# Define canonical class order
labels = [
    "ice phishing scam",
    "nft order scam",
    "address poisoning scam",
    "payable function scam"
]

display_labels = [
    "Ice Phishing",
    "NFT Order",
    "Address Poisoning",
    "Payable Scam"
]

# 2. Compute Classification Metrics
report_dict = classification_report(
    y_true, 
    y_pred, 
    labels=labels, 
    target_names=display_labels, 
    output_dict=True,
    zero_division=0
)

report_df = pd.DataFrame(report_dict).transpose()
report_csv_path = os.path.join("results", "classification_report_500.csv")
report_df.to_csv(report_csv_path)

print("=" * 65)
print("Classification Report (N=500, 125/class):")
print("=" * 65)
print(classification_report(y_true, y_pred, labels=labels, target_names=display_labels, zero_division=0))

# 3. Generate Confusion Matrix Plot
cm = confusion_matrix(y_true, y_pred, labels=labels)

plt.figure(figsize=(8, 6))
sns.heatmap(
    cm, 
    annot=True, 
    fmt="d", 
    cmap="Blues", 
    xticklabels=display_labels, 
    yticklabels=display_labels,
    cbar=False
)

plt.title("PTXPhish Detection Confusion Matrix (N=500)", fontsize=14, pad=15)
plt.xlabel("Predicted Class", fontsize=12, labelpad=10)
plt.ylabel("Ground Truth Class", fontsize=12, labelpad=10)
plt.xticks(rotation=20, ha="right")
plt.yticks(rotation=0)
plt.tight_layout()

cm_png_path = os.path.join("results", "confusion_matrix_500.png")
plt.savefig(cm_png_path, dpi=300)
plt.close()

print("=" * 65)
print(f"Metrics report saved to: {report_csv_path}")
print(f"Confusion Matrix saved to: {cm_png_path}")
print("=" * 65)