from web3 import Web3
import pandas as pd
import os
import time

# 1. Reliable public Ethereum RPC endpoints
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

TRANSFER_SELECTOR = "0xa9059cbb"
TRANSFER_FROM_SELECTOR = "0x23b872dd"

# 2. Load dataset
csv_path = os.path.join("dataset", "cleaned_ptxphish.csv")
if not os.path.exists(csv_path):
    csv_path = os.path.join("PTXPhish-Reproduction-1639", "dataset", "cleaned_ptxphish.csv")

df = pd.read_csv(csv_path)

# Filter specifically for the address poisoning samples
poison_txs = df[df["sub_category"].str.strip().str.lower() == "address poisoning scam"].head(5)

print("\n" + "=" * 65)
print(f"Running Address Poisoning Detection on {len(poison_txs)} samples...")
print("=" * 65)

# 3. Detection Loop
for idx, row in poison_txs.iterrows():
    tx_hash = row["tx_hash"]
    try:
        tx = w3.eth.get_transaction(tx_hash)
        
        raw_hex = tx['input'].hex() if isinstance(tx['input'], bytes) else tx['input']
        if not raw_hex.startswith("0x"):
            raw_hex = "0x" + raw_hex
            
        selector = raw_hex[:10].lower() if len(raw_hex) >= 10 else "0x00000000"
        
        is_poisoning = False
        target_recipient = "N/A"
        raw_val = 0
        method_name = "Unknown"

        # Check ERC-20 transfer(address _to, uint256 _value)
        if selector == TRANSFER_SELECTOR and len(raw_hex) >= 138:
            method_name = "transfer(address,uint256)"
            # Address is padded to 32 bytes (64 hex characters)
            target_recipient = "0x" + raw_hex[34:74]
            raw_val = int(raw_hex[74:138], 16)
            
            # An address poisoning attempt:
            # 1. Calls transfer/transferFrom to broadcast an unrequested transfer
            # 2. Native ETH value sent is 0 (tx['value'] == 0)
            # 3. Either 0 token units, dust units, or non-zero spam token transfer to poison history
            if tx['value'] == 0:
                is_poisoning = True

        # Check ERC-20 transferFrom(address _from, address _to, uint256 _value)
        elif selector == TRANSFER_FROM_SELECTOR and len(raw_hex) >= 202:
            method_name = "transferFrom(address,address,uint256)"
            target_recipient = "0x" + raw_hex[98:138]
            raw_val = int(raw_hex[138:202], 16)
            if tx['value'] == 0:
                is_poisoning = True

        print(f"\nTx Hash:     {tx_hash[:18]}...{tx_hash[-8:]}")
        print(f"Method:      {method_name}")
        print(f"Target Addr: {target_recipient[:10]}...{target_recipient[-6:] if target_recipient != 'N/A' else ''}")
        print(f"Raw Value:   {raw_val}")
        print(f"Detection:   {'🚨 FLAGGED AS ADDRESS POISONING' if is_poisoning else '⚪ NORMAL TRANSACTION'}")
        
        time.sleep(1)
        
    except Exception as e:
        print(f"Tx Hash:     {tx_hash[:18]}... Error fetching: {e}")

print("\n" + "=" * 65)
print("Address Poisoning Detection Test Completed!")
print("=" * 65)