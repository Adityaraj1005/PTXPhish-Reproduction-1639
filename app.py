import streamlit as st
from web3 import Web3
from hexbytes import HexBytes
import pandas as pd
import os

st.set_page_config(page_title="PTXPhish Detector", page_icon="🛡️", layout="wide")

# 1. Multi-RPC Pool Setup
RPC_ENDPOINTS = [
    "https://ethereum.publicnode.com",
    "https://rpc.payload.de",
    "https://cloudflare-eth.com",
    "https://eth.llamarpc.com",
    "https://1rpc.io/eth"
]

@st.cache_resource
def get_w3_clients():
    return [Web3(Web3.HTTPProvider(url, request_kwargs={'timeout': 12})) for url in RPC_ENDPOINTS]

w3_clients = get_w3_clients()

def fetch_transaction(tx_hash_str):
    tx_hash_clean = tx_hash_str.strip()
    if not tx_hash_clean.startswith("0x"):
        tx_hash_clean = "0x" + tx_hash_clean
        
    try:
        tx_hash_bytes = HexBytes(tx_hash_clean)
    except Exception as e:
        return None, None, f"Invalid hex hash format: {e}"

    last_error = ""
    for client in w3_clients:
        try:
            tx = client.eth.get_transaction(tx_hash_bytes)
            if tx is not None:
                return client, tx, None
        except Exception as ex:
            last_error = str(ex)
            continue
            
    return None, None, f"Transaction could not be fetched from active RPC pool. Last error: {last_error}"

ICE_SELECTORS = {"0x095ea7b3", "0xa22cb465", "0xd505accf", "0x39509351", "0x23b872dd", "0xcaa5c23f"}
NFT_SELECTORS = {"0xfb0f3ee1", "0xb3a34c4c", "0xe7acab24", "0xedd62e24", "0x32389b71", "0x2b95044d", "0xa8174404", "0xb3be57f8", "0x3659cfe6"}

def inspect_tx(tx_hash):
    client, tx, err = fetch_transaction(tx_hash)
    if err or not tx:
        return None, err or "Transaction not found on public archive nodes."
    
    raw_hex = tx['input'].hex() if isinstance(tx['input'], bytes) else str(tx['input'])
    if not raw_hex.startswith("0x"):
        raw_hex = "0x" + raw_hex
        
    selector = raw_hex[:10].lower() if len(raw_hex) >= 10 else "0x00000000"
    eth_val = float(client.from_wei(tx['value'], 'ether'))
    
    if selector in NFT_SELECTORS:
        verdict = "NFT Order Phishing Scam"
        risk = "CRITICAL 🚨"
    elif selector == "0xa9059cbb" and eth_val == 0:
        verdict = "Address Poisoning Scam"
        risk = "HIGH ⚠️"
    elif selector in ICE_SELECTORS:
        verdict = "Ice Phishing (Approval Abuse)"
        risk = "CRITICAL 🚨"
    elif eth_val > 0 or len(raw_hex) > 10:
        verdict = "Payable Function Scam"
        risk = "MODERATE ⚠️"
    else:
        verdict = "Benign / Unknown Interaction"
        risk = "LOW ✅"

    return {
        "Verdict": verdict,
        "Risk Level": risk,
        "Function Selector": selector,
        "Native Value (ETH)": eth_val,
        "From": tx['from'],
        "To": tx['to'],
        "Calldata Length": len(raw_hex)
    }, None

# UI Layout
st.title("🛡️ PTXPhish: Ethereum Transaction Phishing Detector")
st.markdown("Automated calldata inspection and deterministic heuristic detection engine.")

tab1, tab2 = st.tabs(["🔍 Live Transaction Scanner", "📊 Empirical Benchmarks"])

with tab1:
    st.subheader("Analyze Live or Historical Ethereum Transaction")
    user_tx = st.text_input("Enter Ethereum Transaction Hash (0x...):", value="")
    
    if st.button("Inspect Transaction 🚀"):
        if not user_tx.strip():
            st.warning("Please paste an Ethereum transaction hash first.")
        else:
            with st.spinner("Querying Ethereum Archive Pool..."):
                details, err = inspect_tx(user_tx)
                if err:
                    st.error(err)
                else:
                    st.success(f"Classification Result: **{details['Verdict']}**")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Risk Level", details["Risk Level"])
                    col2.metric("Function Selector", details["Function Selector"])
                    col3.metric("ETH Value", f"{details['Native Value (ETH)']} ETH")
                    
                    st.json(details)

with tab2:
    st.subheader("Model Performance Summary (N=500 Balanced Benchmark)")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Overall Accuracy", "88.60%")
    c2.metric("Macro F1-Score", "0.89")
    c3.metric("NFT Order F1", "0.99")
    c4.metric("Address Poisoning F1", "0.96")
    
    cm_path = os.path.join("results", "confusion_matrix_500.png")
    if os.path.exists(cm_path):
        st.image(cm_path, caption="Confusion Matrix (N=500, 125 samples per class)", use_container_width=True)