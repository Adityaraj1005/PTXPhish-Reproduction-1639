import pandas as pd
import os

file_path = os.path.join("dataset", "PTXPHISH.xlsx")
if not os.path.exists(file_path):
    file_path = os.path.join("PTXPhish-Reproduction-1639", "dataset", "PTXPHISH.xlsx")

# Load raw sheet without headers
raw = pd.read_excel(file_path, header=None)

print(f"Total Rows: {raw.shape[0]}, Total Columns: {raw.shape[1]}")
print("=" * 60)

# The first 3 rows define the category hierarchy
header_rows = raw.iloc[:3].fillna("")
data_rows = raw.iloc[3:]

categories = []
for col_idx in range(raw.shape[1]):
    level1 = str(header_rows.iloc[0, col_idx]).strip()
    level2 = str(header_rows.iloc[1, col_idx]).strip()
    level3 = str(header_rows.iloc[2, col_idx]).strip()
    
    # Combine levels into a clean label
    parts = [p for p in [level1, level2, level3] if p]
    label = " -> ".join(parts) if parts else f"Column_{col_idx}"
    
    # Count non-empty transaction hashes in this column
    tx_count = data_rows.iloc[:, col_idx].dropna().count()
    categories.append((col_idx, label, tx_count))

print(f"{'Index':<6} | {'Category Hierarchy':<45} | {'Tx Count':<8}")
print("-" * 65)

total_tx = 0
for idx, label, count in categories:
    print(f"{idx:<6} | {label:<45} | {count:<8}")
    total_tx += count

print("=" * 65)
print(f"Total labeled transaction instances: {total_tx}")