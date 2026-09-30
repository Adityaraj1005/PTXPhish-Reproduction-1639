from web3 import Web3
import pandas as pd
import os
import time

# 1. RPC Connection Setup
RPC_ENDPOINTS = [
    "https://ethereum.publicnode.com",
    "https://rpc.payload.de",
    "https://eth.llamarpc.com"
]

w3 = None
for url in RPC_ENDPOINTS:
    temp_w3 = Web3(Web3.HTTPProvider(url))
    try:
        if temp_w3.is_connected():
            w3 = temp_w3
            print(f"[SUCCESS] Connected via {url} 🚀")
            break
    except Exception:
        continue

if not w3:
    print("[ERROR] Could not connect to any RPC endpoint. ❌")
    exit(1)

# 2. Known Function Signatures across all categories
ICE_PHISHING_SELECTORS = [
    "0x095ea7b3",  # approve(address,uint256)
    "0xa22cb465",  # setApprovalForAll(address,bool)
    "0xd505accf",  # permit(...)
    "0x23b872dd",  # transferFrom(address,address,uint256) - spender drain
    "0xcaa5c23f"   # multicall / router batch drain
]

NFT_ORDER_SELECTORS = [
    "0xfb0f3ee1",  # fulfillBasicOrder
    "0xb3a34c4c",  # fulfillOrder
    "0xe7acab24",  # fulfillAdvancedOrder
    "0xedd62e24",  # fulfillAvailableOrders
    "0x32389b71",  # Custom marketplace router
    "0x2b95044d"   # Permit2 permitTransferFrom
]

PAYABLE_SELECTORS = [
    "0x1249c58b",  # mint()
    "0xa0712d68",  # mint(uint256)
    "0x4e71d92d",  # claim()
    "0x379607f5",  # claim(uint256)
    "0xd0e30db0",  # deposit()
    "0x00000000"   # Native ETH transfer
]

def classify_transaction(tx_hash):
    try:
        tx = w3.eth.get_transaction(tx_hash)
        raw_hex = tx['input'].hex() if isinstance(tx['input'], bytes) else tx['input']
        if not raw_hex.startswith("0x"):
            raw_hex = "0x" + raw_hex
            
        selector = raw_hex[:10].lower() if len(raw_hex) >= 10 else "0x00000000"
        eth_val = float(w3.from_wei(tx['value'], 'ether'))

        # Rule 4: NFT Order Phishing
        if selector in NFT_ORDER_SELECTORS and eth_val == 0:
            return "NFT order scam"

        # Rule 1: Ice Phishing (Explicit approval, permit, transferFrom, or multicall drain)
        if selector in ICE_PHISHING_SELECTORS:
            return "Ice phishing scam"

        # Rule 3: Address Poisoning (Direct transfer called to spam victim's history)
        if selector == "0xa9059cbb" and eth_val == 0:
            return "address poisoning scam"

        # Rule 2: Payable Function Abuse (ETH sent with call)
        if eth_val > 0:
            return "payable function scam"

        return "unknown"

    except Exception as e:
        return f"error: {str(e)[:30]}"

# 3. Load dataset
csv_path = os.path.join("dataset", "cleaned_ptxphish.csv")
if not os.path.exists(csv_path):
    csv_path = os.path.join("PTXPhish-Reproduction-1639", "dataset", "cleaned_ptxphish.csv")

df = pd.read_csv(csv_path)

# Sample 5 transactions per category (20 total)
sampled_df = df.groupby("sub_category", as_index=False, group_keys=False).apply(
    lambda x: x.head(5)
).reset_index(drop=True)

print("=" * 70)
print(f"Starting Batch Evaluation on {len(sampled_df)} sample transactions... 🧪")
print("=" * 70)

results = []

for idx, row in sampled_df.iterrows():
    tx_hash = row["tx_hash"]
    ground_truth = str(row["sub_category"]).strip()
    
    predicted = classify_transaction(tx_hash)
    is_match = (predicted.lower() == ground_truth.lower())
    
    results.append({
        "tx_hash": tx_hash,
        "ground_truth": ground_truth,
        "predicted": predicted,
        "correct": is_match
    })
    
    status = "✅ MATCH" if is_match else f"❌ MISMATCH (Pred: {predicted})"
    print(f"[{idx+1:02d}/{len(sampled_df)}] {ground_truth[:18]:<18} -> {status}")
    
    time.sleep(0.8)

# 4. Output summary and metrics
results_df = pd.DataFrame(results)
output_dir = "results"
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "batch_evaluation_sample.csv")
results_df.to_csv(output_file, index=False)

correct_count = results_df["correct"].sum()
accuracy = (correct_count / len(results_df)) * 100

print("\n" + "=" * 70)
print("Batch Evaluation Complete! 🎉")
print(f"Total Evaluated: {len(results_df)}")
print(f"Correct Predictions: {correct_count}/{len(results_df)}")
print(f"Sample Accuracy: {accuracy:.2f}%")
print(f"Detailed results saved to: {output_file}")
print("=" * 70)