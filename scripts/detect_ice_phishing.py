from web3 import Web3
import pandas as pd
import os
import time

# 1. Reliable free public Ethereum mainnet RPC endpoints
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
            print(f"[SUCCESS] Connected via {url}")
            break
    except Exception:
        continue

if not w3:
    print("[ERROR] Could not connect to any RPC endpoint.")
    exit(1)

# 2. Known Function Signatures used in Ice Phishing / Token Drain scams
KNOWN_SELECTORS = {
    "0x095ea7b3": "approve(address,uint256) - ERC20 Approval",
    "0xa22cb465": "setApprovalForAll(address,bool) - ERC721/1155 Full Access",
    "0xd505accf": "permit(...) - Gasless Token Allowance",
    "0x23b872dd": "transferFrom(address,address,uint256) - Draining Approved Tokens",
    "0xcaa5c23f": "multicall(tuple[]) - Batch Attack / Drainer Router"
}

# 3. Load our cleaned dataset
csv_path = os.path.join("dataset", "cleaned_ptxphish.csv")
if not os.path.exists(csv_path):
    csv_path = os.path.join("PTXPhish-Reproduction-1639", "dataset", "cleaned_ptxphish.csv")

df = pd.read_csv(csv_path)

# Filter for Ice Phishing transactions and take the first 5 for testing
ice_txs = df[df["sub_category"].str.contains("Ice phishing", case=False, na=False)].head(5)

print("\n" + "=" * 60)
print(f"Running Ice Phishing Detection Test on {len(ice_txs)} samples...")
print("=" * 60)

# 4. Process each transaction
for idx, row in ice_txs.iterrows():
    tx_hash = row["tx_hash"]
    try:
        tx = w3.eth.get_transaction(tx_hash)
        
        # Standardize hex input so it always begins with '0x'
        raw_hex = tx['input'].hex() if isinstance(tx['input'], bytes) else tx['input']
        if not raw_hex.startswith("0x"):
            raw_hex = "0x" + raw_hex
        
        # Ethereum function selector is exactly 4 bytes (0x + 8 characters = 10 chars)
        selector = raw_hex[:10].lower()

        matched_method = KNOWN_SELECTORS.get(selector, "Unknown / Other Method")
        is_flagged = selector in KNOWN_SELECTORS
        
        print(f"\nTx Hash:   {tx_hash[:18]}...{tx_hash[-8:]}")
        print(f"Selector:  {selector} -> {matched_method}")
        print(f"Detection: {'🚨 FLAGGED AS ICE PHISHING' if is_flagged else '⚪ NOT FLAGGED'}")
        
        # Small delay to respect public node rate limits
        time.sleep(1)
        
    except Exception as e:
        print(f"Tx Hash:   {tx_hash[:18]}... Error fetching: {e}")

print("\n" + "=" * 60)
print("Test completed successfully!")
print("=" * 60)