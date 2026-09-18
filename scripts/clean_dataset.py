import pandas as pd
import os

file_path = os.path.join("dataset", "PTXPHISH.xlsx")
if not os.path.exists(file_path):
    file_path = os.path.join("PTXPhish-Reproduction-1639", "dataset", "PTXPHISH.xlsx")

# Load the raw spreadsheet
raw = pd.read_excel(file_path, header=None)

# Fill merged cells across rows 0, 1, and 2
header_df = raw.iloc[:3].ffill(axis=1).fillna("")

records = []
category_summary = {}

for col_idx in range(raw.shape[1]):
    l1 = str(header_df.iloc[0, col_idx]).strip()
    l2 = str(header_df.iloc[1, col_idx]).strip()
    l3 = str(header_df.iloc[2, col_idx]).strip()
    
    label = f"{l1} | {l2} | {l3}".strip(" |")
    
    # Extract transaction hashes (ignoring empty cells)
    hashes = raw.iloc[3:, col_idx].dropna().tolist()
    
    # Determine if benign or phishing
    is_phish = 0 if any(b in label.lower() for b in ["benign", "normal", "legitimate tx"]) else 1
    
    for h in hashes:
        h_str = str(h).strip()
        if h_str.startswith("0x") and len(h_str) == 66:
            records.append({
                "tx_hash": h_str,
                "label": label,
                "is_phishing": is_phish,
                "category": l2 if l2 else l1,
                "sub_category": l3
            })
            category_summary[label] = category_summary.get(label, 0) + 1

# Create unified dataframe
df_clean = pd.DataFrame(records)

print("=" * 60)
print(f"Total Valid Ethereum Transactions Extracted: {len(df_clean)}")
print(f"Phishing Transactions: {(df_clean['is_phishing'] == 1).sum()}")
print(f"Benign Transactions:   {(df_clean['is_phishing'] == 0).sum()}")
print("=" * 60)

print("\nSample Category Summary:")
for cat, count in list(category_summary.items())[:10]:
    print(f" - {cat}: {count}")

# Save clean CSV
output_csv = os.path.join("dataset", "cleaned_ptxphish.csv")
df_clean.to_csv(output_csv, index=False)
print(f"\n[SUCCESS] Clean dataset saved to: {output_csv}")