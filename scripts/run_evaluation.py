from web3 import Web3
import pandas as pd
import os
import time
from collections import Counter

# 1. Multi-RPC Pool for reliable archive access
RPC_ENDPOINTS = [
    "https://ethereum.publicnode.com",
    "https://rpc.payload.de",
    "https://cloudflare-eth.com"
]

w3_clients = [Web3(Web3.HTTPProvider(url, request_kwargs={'timeout': 10})) for url in RPC_ENDPOINTS]

def fetch_transaction_with_failover(tx_hash):
    """Tries each RPC node sequentially if one drops or times out"""
    for client in w3_clients:
        try:
            tx = client.eth.get_transaction(tx_hash)
            if tx:
                return client, tx
        except Exception:
            continue
    return None, None

# 2. Heuristic Signatures Registry (ORIGINAL 88.6% lists, untouched)
ICE_PHISHING_SELECTORS = {
    "0x095ea7b3",  # approve(address,uint256)
    "0xa22cb465",  # setApprovalForAll(address,bool)
    "0xd505accf",  # permit(...)
    "0x39509351",  # increaseAllowance(address,uint256)
    "0x23b872dd",  # transferFrom(address,address,uint256)
    "0xcaa5c23f",  # multicall batch drain sweep
    "0x42842e0e",  # safeTransferFrom(address,address,uint256)  [21 errors fixed]
    "0x36c78516",  # Permit2 transferFrom                        [3 errors fixed]
    "0x0d58b1db",  # Permit2 batch transferFrom                  [5 errors fixed]
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
    "0x3659cfe6",  # Batch fulfillment sweep
    "0x9a1fc3a7",  # Blur execute
}

# Selectors where "value > 0" means the approval is fake (native ETH drain)
APPROVAL_ONLY_SELECTORS = {"0x095ea7b3", "0xa22cb465", "0x39509351", "0xd505accf"}


def arg_word(raw_hex, i):
    """i-th 32-byte argument after the selector; None if calldata is too short."""
    start = 10 + 64 * i
    word = raw_hex[start:start + 64]
    return int(word, 16) if len(word) == 64 else None


LAST_EXTRA = {}

def classify_detail(tx_hash):
    """Returns (label, selector, eth_val)."""
    client, tx = fetch_transaction_with_failover(tx_hash)
    if not tx:
        return "error: tx_not_found", "none", 0.0

    raw_hex = tx['input'].hex() if isinstance(tx['input'], bytes) else str(tx['input'])
    if not raw_hex.startswith("0x"):
        raw_hex = "0x" + raw_hex
    raw_hex = raw_hex.lower()

    selector = raw_hex[:10] if len(raw_hex) >= 10 else "0x00000000"
    eth_val = float(client.from_wei(tx['value'], 'ether'))
    amt_idx = 2 if selector == "0x23b872dd" else 1
    LAST_EXTRA[tx_hash] = {
        "amount": arg_word(raw_hex, amt_idx),
        "to": str(tx.get('to')),
        "input_len": len(raw_hex),
    }

    # 1. NFT Order Phishing  (original)
    if selector in NFT_ORDER_SELECTORS:
        return "NFT order scam", selector, eth_val

    # 2. Address Poisoning (original rule)
    if selector == "0xa9059cbb" and eth_val == 0:
        return "address poisoning scam", selector, eth_val

    # 2c. NEW: in this dataset approve() is labelled payable, never Ice (0 Ice approve rows)
    if selector == "0x095ea7b3":
        return "payable function scam", selector, eth_val

    # 2d. NEW: empty calldata + zero ETH -> address poisoning
    if raw_hex == "0x" and eth_val == 0:
        return "address poisoning scam", selector, eth_val

    # 2b. NEW: zero-amount transferFrom + no ETH -> Address Poisoning
    #     (runs only for transferFrom, so approve/permit/etc. are untouched)
    if selector == "0x23b872dd" and eth_val == 0 and arg_word(raw_hex, 2) == 0:
        return "address poisoning scam", selector, eth_val

    # 3a. NEW: fake approval that carries native ETH -> Payable
    if selector in APPROVAL_ONLY_SELECTORS and eth_val > 0:
        return "payable function scam", selector, eth_val

    # 3. Ice Phishing (original)
    if selector in ICE_PHISHING_SELECTORS:
        return "Ice phishing scam", selector, eth_val

    # 4. Payable Function Scam (original)
    if eth_val > 0 or len(raw_hex) >= 10:  # NEW: selector-only calls count too
        return "payable function scam", selector, eth_val

    return "unknown", selector, eth_val


def classify_transaction(tx_hash):
    return classify_detail(tx_hash)[0]


# 3. Load dataset
csv_path = os.path.join("dataset", "cleaned_ptxphish.csv")
if not os.path.exists(csv_path):
    csv_path = os.path.join("PTXPhish-Reproduction-1639", "dataset", "cleaned_ptxphish.csv")

df = pd.read_csv(csv_path)

# Sample 125 balanced transactions per class (Total = 500)
SAMPLES_PER_CLASS = 125
sampled_df = df.groupby("sub_category", as_index=False, group_keys=False).apply(
    lambda x: x.sample(n=min(len(x), SAMPLES_PER_CLASS), random_state=7)
).reset_index(drop=True)

total_txs = len(sampled_df)
print("=" * 80)
print(f"Running Large-Scale Benchmark on {total_txs} transactions ({SAMPLES_PER_CLASS}/class)...")
print("=" * 80)

results = []
correct_count = 0

for idx, row in sampled_df.iterrows():
    tx_hash = row["tx_hash"]
    ground_truth = str(row["sub_category"]).strip()

    predicted, selector, eth_val = classify_detail(tx_hash)
    is_match = (predicted.lower() == ground_truth.lower())
    if is_match:
        correct_count += 1

    results.append({
        "tx_hash": tx_hash,
        "ground_truth": ground_truth,
        "predicted": predicted,
        "selector": selector,
        "eth_val": eth_val,
        "amount": LAST_EXTRA.get(tx_hash, {}).get("amount"),
        "to": LAST_EXTRA.get(tx_hash, {}).get("to"),
        "input_len": LAST_EXTRA.get(tx_hash, {}).get("input_len"),
        "correct": is_match
    })

    status = "MATCH" if is_match else f"MISMATCH (Pred: {predicted})"
    print(f"[{idx+1:03d}/{total_txs}] {ground_truth[:20]:<20} -> {status}")

    time.sleep(0.2)

# 4. Save results
results_df = pd.DataFrame(results)
output_dir = "results"
os.makedirs(output_dir, exist_ok=True)
output_file = os.path.join(output_dir, "large_evaluation_benchmark_500.csv")
results_df.to_csv(output_file, index=False)

accuracy = (correct_count / total_txs) * 100

# 5. Metrics
results_df["gt_l"] = results_df["ground_truth"].str.lower()
results_df["pr_l"] = results_df["predicted"].str.lower()
f1s = []
print("\nPer-class metrics:")
for c in sorted(results_df["gt_l"].unique()):
    tp = ((results_df.gt_l == c) & (results_df.pr_l == c)).sum()
    fp = ((results_df.gt_l != c) & (results_df.pr_l == c)).sum()
    fn = ((results_df.gt_l == c) & (results_df.pr_l != c)).sum()
    p = tp / (tp + fp) if tp + fp else 0
    r = tp / (tp + fn) if tp + fn else 0
    f = 2 * p * r / (p + r) if p + r else 0
    f1s.append(f)
    print(f"  {c:<26} P={p:.3f} R={r:.3f} F1={f:.3f}")

print("\n" + "=" * 80)
print("Large Benchmark Complete!")
print(f"Total Transactions Evaluated: {total_txs}")
print(f"Correct Predictions:          {correct_count} / {total_txs}")
print(f"Overall Accuracy:             {accuracy:.2f}%")
print(f"Macro F1:                     {sum(f1s)/len(f1s):.4f}")
print(f"Full benchmark data saved to: {output_file}")
print("=" * 80)

print("\nConfusion matrix (rows = truth, cols = predicted):")
print(pd.crosstab(results_df["ground_truth"], results_df["predicted"]))

# 6. DIAGNOSTIC: which selectors cause the mistakes? (use this to extend the lists)
wrong = results_df[~results_df["correct"]]
print("\nTop selectors in MISMATCHES  (truth -> predicted : selector : count)")
cnt = Counter(zip(wrong["ground_truth"], wrong["predicted"], wrong["selector"]))
for (gt, pr, sel), n in cnt.most_common(25):
    print(f"  {gt:<24} -> {pr:<24} {sel}  x{n}")

# 7. DIAGNOSTIC 2: inspect the remaining hard cases (approve / transfer / transferFrom)
hard = results_df[results_df["selector"].isin(["0x095ea7b3", "0xa9059cbb", "0x23b872dd"])]
print("\nSelector x truth breakdown (amount==0 count, eth>0 count):")
for (sel, gt), g in hard.groupby(["selector", "ground_truth"]):
    print(f"  {sel} {gt:<24} n={len(g):<3} amount==0:{(g.amount == 0).sum():<3} eth>0:{(g.eth_val > 0).sum():<3} "
          f"median_input_len={int(g.input_len.median())}")
print("\nMismatched rows for these selectors:")
print(hard[~hard["correct"]][["ground_truth", "predicted", "selector", "amount", "eth_val", "input_len", "to"]].to_string())