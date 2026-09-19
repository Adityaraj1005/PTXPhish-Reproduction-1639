from web3 import Web3
import pandas as pd
import os

# Reliable free public Ethereum mainnet RPC endpoints
RPC_ENDPOINTS = [
    "https://eth.llamarpc.com",
    "https://ethereum.publicnode.com",
    "https://rpc.payload.de"
]

w3 = None
for url in RPC_ENDPOINTS:
    print(f"Trying connection to: {url}...")
    temp_w3 = Web3(Web3.HTTPProvider(url))
    try:
        block = temp_w3.eth.block_number
        print(f"[SUCCESS] Connected via {url} | Latest Block: {block}")
        w3 = temp_w3
        break
    except Exception as e:
        print(f"Failed ({e}), trying next...")

if not w3:
    print("[ERROR] Could not connect to any RPC endpoint.")
    exit(1)

# Load dataset and pick the first Ice Phishing transaction
csv_path = os.path.join("dataset", "cleaned_ptxphish.csv")
if not os.path.exists(csv_path):
    csv_path = os.path.join("PTXPhish-Reproduction-1639", "dataset", "cleaned_ptxphish.csv")

df = pd.read_csv(csv_path)

sample_tx = df[df["sub_category"].str.contains("Ice phishing", case=False, na=False)].iloc[0]
sample_hash = sample_tx["tx_hash"]

print("\n" + "=" * 55)
print(f"Target Scam Category: {sample_tx['sub_category']}")
print(f"Target Hash:          {sample_hash}")
print("=" * 55)

# Fetch transaction directly from Ethereum
tx = w3.eth.get_transaction(sample_hash)

print(f"From (Victim):        {tx['from']}")
print(f"To (Scam Contract):   {tx['to']}")
print(f"Value:                {w3.from_wei(tx['value'], 'ether')} ETH")
print(f"Method Selector:      {tx['input'][:10].hex() if isinstance(tx['input'], bytes) else tx['input'][:10]}")
print(f"Full Input Length:    {len(tx['input'])} hex characters")
print("=" * 55)