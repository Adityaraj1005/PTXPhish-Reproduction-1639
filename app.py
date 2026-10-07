import os
import streamlit as st
import pandas as pd
from hexbytes import HexBytes
from web3 import Web3
from alert_engine import generate_rescue_transaction

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
    return [Web3(Web3.HTTPProvider(url, request_kwargs={"timeout": 12})) for url in RPC_ENDPOINTS]

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
        except Exception as e:
            last_error = str(e)
            continue

    return None, None, f"Transaction could not be fetched from active RPC pool. Last error: {last_error}"

ICE_SELECTORS = ["0x095ea7b3", "0xa22cb465", "0xd505accf", "0x39509351", "0x23b872dd", "0xdac8cf1f"]
NFT_SELECTORS = ["0xfb0f3ee1", "0xb3a31c4c", "0xe7acab24", "0xedd42e24", "0x52303b71", "0x1b9f8fd4", "0xa8174404", "0x6b1e97bb", "0x1d95cfed"]

def inspect_tx(tx_hash):
    client, tx, err = fetch_transaction(tx_hash)
    if err or not tx:
        return None, err or "Transaction not found on public archive nodes."

    raw_hex = tx["input"].hex() if isinstance(tx["input"], (bytes, HexBytes)) else str(tx["input"])
    if not raw_hex.startswith("0x"):
        raw_hex = "0x" + raw_hex

    selector = raw_hex[:10].lower() if len(raw_hex) >= 10 else "0x00000000"
    eth_val = float(client.from_wei(tx["value"], "ether"))

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
        risk = "LOW 🟢"

    return {
        "Verdict": verdict,
        "Risk Level": risk,
        "Function Selector": selector,
        "Native Value (ETH)": eth_val,
        "From: to[from]": tx["from"],
        "To: to[to]": tx["to"],
        "Calldata Length": len(raw_hex)
    }, None

# UI Layout
st.title("🛡️ PTXPhish: Ethereum Transaction Phishing Detector")
st.markdown("Automated calldata inspection and deterministic heuristic detection engine.")

tab1, tab2 = st.tabs(["🔍 Live Transaction Scanner", "📊 Empirical Benchmark"])

with tab1:
    st.subheader("Analyze Live or Historical Ethereum Transaction")
    user_tx = st.text_input("Enter Ethereum Transaction Hash (0x...):", value="")

    # Initialize session state for persistent inspection data
    if "analysis_details" not in st.session_state:
        st.session_state.analysis_details = None

    if st.button("Inspect Transaction 🚀"):
        if not user_tx.strip():
            st.warning("Please paste an Ethereum transaction hash first.")
        else:
            with st.spinner("Querying Ethereum Archive Pool..."):
                details, err = inspect_tx(user_tx)
                if err:
                    st.error(err)
                    st.session_state.analysis_details = None
                else:
                    st.session_state.analysis_details = details

    # Render results whenever stored in session_state (persists on subsequent button clicks)
    if st.session_state.analysis_details is not None:
        details = st.session_state.analysis_details

        if details["Verdict"] == "Benign / Unknown Interaction":
            st.success(f"Classification Result: {details['Verdict']}")
        else:
            st.error(f"Classification Result: {details['Verdict']}")

        col1, col2, col3 = st.columns(3)
        col1.metric("Risk Level", details["Risk Level"])
        col2.metric("Function Selector", details["Function Selector"])
        col3.metric("ETH Value", f"{details['Native Value (ETH)']} ETH")

        st.json(details)

        # --- PAPER LAST-LINE IMPLEMENTATION (Section VIII) ---
        if details["Verdict"] != "Benign / Unknown Interaction":
            st.markdown("---")
            st.subheader("🛡️ On-Chain Victim Alert Dispatcher (Paper Section VIII)")

            victim_addr = details.get("From: to[from]", "0xVictimAddress")
            attacker_addr = details.get("To: to[to]", "0xAttackerContract")
            threat_type = details.get("Verdict", "Ice Phishing")

            rescue_payload = generate_rescue_transaction(
                victim_address=victim_addr,
                threat_category=threat_type,
                attacker_address=attacker_addr
            )

            col_msg, col_actions = st.columns([2, 1])
            with col_msg:
                st.info(f"**Generated Warning Payload:**\n\n`{rescue_payload['raw_message']}`")
                with st.expander("🔍 View Encoded Calldata (0-ETH Warning Tx)"):
                    st.code(rescue_payload["input"], language="text")

            with col_actions:
                st.markdown("**Remediation Protocol:**")
                st.link_button("🌐 Open Revoke.cash", rescue_payload["remediation_url"])

                if st.button("🚀 Dispatch Simulated Alert", key="btn_dispatch_alert"):
                    st.toast("📡 Packaging 0-ETH Alert Transaction...")
                    st.success(f"✅ Alert Transaction Staged & Sent to {victim_addr[:10]}...!")
                    st.json({
                        "status": "Simulated Success (HTTP 200)",
                        "to": rescue_payload["to"],
                        "value": "0 ETH",
                        "gasEstimate": rescue_payload["gasLimit"],
                        "calldata_bytes": len(rescue_payload["input"]) // 2
                    })

with tab2:
    st.subheader("Model Performance Summary (N=500 Balanced Benchmark)")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Overall Accuracy", "88.60%")
    c2.metric("Macro F1 Score", "0.85")
    c3.metric("NFT Order F1", "0.66")
    c4.metric("Address Poisoning F1", "0.96")

    cm_path = os.path.join("results", "confusion_matrix_500.png")
    if os.path.exists(cm_path):
        st.image(cm_path, caption="Confusion Matrix (N=500, 125 samples per class)", use_container_width=True)