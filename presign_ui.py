"""Streamlit UI for presign.py. In app.py add:   import presign_ui; presign_ui.render()"""
import streamlit as st
import presign

COLORS = {"LOW": "green", "MODERATE": "orange", "HIGH": "red", "CRITICAL": "red"}

_SPENDER = "0" * 24 + "ab" * 20
_OTHER = "0" * 24 + "cd" * 20
_USDC = "0xA0b86991c6218b36c1d19d4a2e9Eb0cE3606eB48"

# name -> (calldata, ETH value, to address)
EXAMPLES = {
    "Choose an example...": ("", 0.0, ""),
    "Unlimited approve (scam-style)": ("0x095ea7b3" + _SPENDER + "f" * 64, 0.0, _USDC),
    "Limited approve": ("0x095ea7b3" + _SPENDER + "0" * 63 + "1", 0.0, _USDC),
    "Revoke an approval (safe)": ("0x095ea7b3" + _SPENDER + "0" * 64, 0.0, _USDC),
    "NFT: setApprovalForAll(true)": ("0xa22cb465" + _SPENDER + "0" * 63 + "1", 0.0, ""),
    "Zero-value transfer (address poisoning)": ("0xa9059cbb" + _SPENDER + "0" * 64, 0.0, _USDC),
    "Normal token transfer": ("0xa9059cbb" + _SPENDER + "0" * 63 + "1", 0.0, _USDC),
    "Fake 'claim' airdrop taking 0.1 ETH": ("0x4e71d92d", 0.1, ""),
    "Plain ETH send": ("0x", 0.5, ""),
}

ADDRESS_EXAMPLES = {
    "Choose an example...": ("", ""),
    "Lookalike pair (same first 4 and last 4)": ("0xa7B4BAC8f0f9692e56750aEFB5f6cB5516E90570",
                                                 "0xa7b4" + "1" * 32 + "0570"),
    "Completely different addresses": ("0xa7B4BAC8f0f9692e56750aEFB5f6cB5516E90570", "0x" + "11" * 20),
    "Same address": ("0xa7B4BAC8f0f9692e56750aEFB5f6cB5516E90570", "0xa7b4bac8f0f9692e56750aefb5f6cb5516e90570"),
}


def _load_example():
    data, value, to = EXAMPLES[st.session_state["ps_example"]]
    st.session_state["ps_calldata"], st.session_state["ps_value"], st.session_state["ps_to"] = data, value, to


def _load_address_example():
    a, b = ADDRESS_EXAMPLES[st.session_state["la_example"]]
    st.session_state["la_a"], st.session_state["la_b"] = a, b


def render():
    st.header("Should I sign this?")
    st.caption("Paste what your wallet is asking you to sign. Nothing is sent anywhere: this runs offline.")
    tab1, tab2 = st.tabs(["Check a transaction", "Compare two addresses"])

    with tab1:
        st.selectbox("Try an example (or paste your own below)", list(EXAMPLES), key="ps_example",
                     on_change=_load_example)
        calldata = st.text_area("Calldata (hex data from the wallet pop-up)", key="ps_calldata",
                                placeholder="0x095ea7b3000000...", height=110)
        c1, c2 = st.columns(2)
        value = c1.number_input("ETH value", min_value=0.0, format="%.6f", key="ps_value")
        to = c2.text_input("To address (optional)", key="ps_to")
        if st.button("Analyze", key="presign_go"):
            try:
                res = presign.analyze(calldata, value, to or None)
                colour = COLORS[res["risk"]]
                st.markdown(f"### :{colour}[{res['risk']}] - {res['title']}")
                st.write(res["explanation"])
                st.markdown("**Why:** " + "; ".join(res["reasons"]))
                if "spender" in res["details"]:
                    st.markdown(f"Spender: `{res['details']['spender']}`")
                st.caption(f"Category: {res['category']} | Selector: {res['selector']}")
                if res["risk"] in ("HIGH", "CRITICAL"):
                    st.warning("If you already signed something similar, revoke it at https://revoke.cash")
                st.caption("LOW means no suspicious pattern was recognised, not that the transaction is proven safe.")
            except ValueError as e:
                st.error(str(e))

    with tab2:
        st.selectbox("Try an example (or paste your own below)", list(ADDRESS_EXAMPLES), key="la_example",
                     on_change=_load_address_example)
        a = st.text_input("Address from your history", key="la_a")
        b = st.text_input("Address in the new transaction", key="la_b")
        if st.button("Compare", key="la_go"):
            try:
                r = presign.lookalike(a, b)
                (st.error if r["lookalike"] else st.info)(r["verdict"])
                md = presign.render_lookalike_markdown(r)
                if md:
                    st.markdown(md)
            except ValueError as e:
                st.error(str(e))