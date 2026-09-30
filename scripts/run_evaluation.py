from web3 import Web3
import pandas as pd
import os
import time

# 1. Multi-RPC Pool for reliable archive access
RPC_ENDPOINTS = [
    "https://ethereum.publicnode.com",
    "https://rpc.payload.de",
    "https://cloudflare-eth.com"
]

w3_clients = [Web3(Web3.HTTPProvider(url, request_kwargs={'timeout': 10})) for url in RPC_ENDPOINTS]

def fetch_transaction_with_failover(tx_hash):
    for client in w3_clients:
        try:
            tx = client.eth.get_transaction(tx_hash)
            if tx:
                return client, tx
        except Exception:
            continue
    return None, None

# 2. Heuristic Signatures Registry
ICE_PHISHING_SELECTORS = {
    "0x095ea7b3",  # approve(address,uint256)
    "0xa22cb465",  # setApprovalForAll(address,bool)
    "0xd505accf",  # permit(...)
    "0x39509351",  # increaseAllowance(address,uint256)
    "0x23b872dd",  # transferFrom(address,address,uint256)
    "0xcaa5c23f"   # multicall batch drain sweep
}

NFT_ORDER_SELECTORS = {
    "0xfb0f3ee1",  # fulfillBasicOrder
    "0xb3a34c4c",  # fulfillOrder
    "0xe7acab24",  # fulfillAdvancedOrder
    "0xedd62e24",  # fulfillAvailableOrders
    "0x32389b71",  # Marketplace router
    "0x2b95044d",  # Permit2 permitTransferFrom
    "0xa8174404",  # matchOrders / Blur execution
    "0xb3be57f8",  # Seaport order execution
    "0x3659cfe6"   # Batch fulfillment sweep
}

def classify_transaction(tx_hash):
    client, tx = fetch_transaction_with_failover(tx_hash)
    if not tx:
        return "error: tx_not_found"

    raw_hex = tx['input'].hex() if isinstance(tx['input'], bytes) else str(tx['input'])
    if not raw_hex.startswith("0x"):
        raw_hex = "0x" + raw_hex
        
    selector = raw_hex[:10].lower() if len(raw_hex) >= 10 else "0x00000000"
    eth_val = float(client.from_wei(tx['value'], 'ether'))

    # 1. NFT Order Phishing (marketplace fulfillment)
    if selector in NFT_ORDER_SELECTORS:
        return "NFT order scam"

    # 2. Address Poisoning (zero-ETH direct transfer spam)
    if selector == "0xa9059cbb" and eth_val == 0:
        return "address poisoning scam"

    # 3. Ice Phishing (approval delegation, permits, spender drain sweeps)
    if selector in ICE_PHISHING_SELECTORS:
        return "Ice phishing scam"

    # 4. Payable Function Scam (interactive contract traps, router multicalls, or non-zero ETH)
    if eth_val > 0 or len(raw_hex) > 10:
        return "payable function scam"

    return "unknown"

# 3. Load dataset
csv_path = os.path.join("dataset", "cleaned_ptxphish.csv")
if not os.path.exists(csv_path):
    csv_path = os.path.join("PTXPhish-Reproduction-1639", "dataset", "cleaned_ptxphish.csv")

df = pd.read_csv(csv_path)

# Sample 25 balanced transactions per class with fixed random seed
SAMPLES_PER_CLASS = 25
sampled_df = df.groupby("sub_category", as_index=False, group_keys=False).apply(
    lambda x: x.sample(n=min(len(x), SAMPLES_PER_CLASS), random_state=42)
).reset_index(drop=True)

total_txs = len(sampled_df)
print("=" * 75)
print(f"Running Benchmark on {total_txs} transactions ({SAMPLES_PER_CLASS}/class)...")
print("=" * 75)

results = []
correct_count = 0

for idx, row in sampled_df.iterrows():
    tx_hash = row["tx_hash"]
    ground_truth = str(row["sub_category"]).strip()
    
    predicted = classify_transaction(tx_hash)
    is_match = (predicted.lower() == ground_truth.lower())
    if is_match:
        correct_count += 1
    
    results.append({
        "tx_hash": tx_hash,
        "ground_truth": ground_truth,
        "predicted": predicted,
        "correct": is_match
    })
    
    status = "✅ MATCH" if is_match else f"❌ MISMATCH (Pred: {predicted})"
    print(f"[{idx+1:03d}/{total_txs}] {ground_truth[:20]:<20} -> {status}")
    
    time.sleep(0.35)

# 4. Save results
results_df = pd.DataFrame(results)
output_dir = "results"
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "large_evaluation_benchmark_100.csv")
results_df.to_csv(output_file, index=False)

accuracy = (correct_count / total_txs) * 100

print("\n" + "=" * 75)
print("Benchmark Complete!")
print(f"Total Transactions Evaluated: {total_txs}")
print(f"Correct Predictions:          {correct_count} / {total_txs}")
print(f"Overall Accuracy:             {accuracy:.2f}%")
print(f"Full benchmark data saved to: {output_file}")
print("=" * 75)