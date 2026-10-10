"""Streamlit UI for presign.py. In app.py add:   import presign_ui; presign_ui.render()"""
import streamlit as st
import presign

COLORS = {"LOW": "green", "MODERATE": "orange", "HIGH": "red", "CRITICAL": "red"}


def render():
    st.header("Should I sign this?")
    st.caption("Paste what your wallet is asking you to sign. Nothing is sent anywhere: this runs offline.")
    tab1, tab2 = st.tabs(["Check a transaction", "Compare two addresses"])

    with tab1:
        calldata = st.text_area("Calldata (hex data from the wallet pop-up)", placeholder="0x095ea7b3000000...", height=110)
        c1, c2 = st.columns(2)
        value = c1.number_input("ETH value", min_value=0.0, value=0.0, format="%.6f")
        to = c2.text_input("To address (optional)")
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