"""
presign.py - "Should I sign this?" checker for Ethereum transactions.
Pure Python, fully offline: reads only the calldata + ETH value you paste (no RPC, no API keys).

Public API
    analyze(calldata, value_eth=0.0, to=None) -> dict   verdict + plain-English explanation
    lookalike(addr_a, addr_b, n=4)            -> dict   address-poisoning similarity check
"""
import re

UNLIMITED = 2 ** 255          # amounts above this are treated as "unlimited"
RISK_ORDER = {"LOW": 0, "MODERATE": 1, "HIGH": 2, "CRITICAL": 3}

# ---- selector registry (names from the project + paper Table X for payable scams) ----------
APPROVE, INCREASE, SET_ALL, PERMIT = "0x095ea7b3", "0x39509351", "0xa22cb465", "0xd505accf"
TRANSFER, TRANSFER_FROM, SAFE_TRANSFER_FROM = "0xa9059cbb", "0x23b872dd", "0x42842e0e"
PERMIT2 = {"0x2b67b570": "Permit2 permit", "0x2a2d80d1": "Permit2 permit (batch)",
           "0x36c78516": "Permit2 transferFrom", "0x0d58b1db": "Permit2 transferFrom (batch)",
           "0x2b95044d": "Permit2 permitTransferFrom"}
NFT_ORDERS = {"0xfb0f3ee1": "Seaport fulfillBasicOrder", "0xb3a34c4c": "Seaport fulfillOrder",
              "0xe7acab24": "Seaport fulfillAdvancedOrder", "0xedd62e24": "Seaport fulfillAvailableOrders",
              "0x32389b71": "marketplace router", "0xa8174404": "matchOrders / Blur execution",
              "0xb3be57f8": "Seaport order execution", "0x3659cfe6": "batch fulfilment",
              "0x9a1fc3a7": "Blur execute"}
MULTICALL = {"0xac9650d8", "0x5ae401dc", "0x1f0464d1", "0x252dba42", "0x82ad56cb", "0xcaa5c23f", "0x3593564c"}
PAYABLE_TRAPS = {  # sensitive function names listed in Table X of the paper
    "0x5fba79f5": "SecurityUpdate", "0xaf347b61": "SecurityUpdate", "0x62929a1e": "ConnectWallet",
    "0x9c9316c5": "NetworkMerge", "0x1b9265b8": "pay", "0x4e71d92d": "claim", "0x3158952e": "claim",
    "0xaad3ec96": "claim", "0x0c7ef932": "claim", "0xb88a802f": "claimReward", "0x79372f9a": "claimReward",
    "0xaf7ec6cb": "claimReward", "0x63e32091": "claimReward", "0xef5cfb8c": "claimRewards",
    "0x4185f8eb": "receiveETH"}
EMBED_APPROVALS = [s[2:] for s in (APPROVE, INCREASE, SET_ALL, PERMIT)]


# ---- parsing helpers -------------------------------------------------------------------------
def clean_hex(raw):
    raw = (raw or "").strip().replace(" ", "").replace("\n", "").lower()
    if raw in ("", "0x"):
        return "0x"
    if not raw.startswith("0x"):
        raw = "0x" + raw
    if not re.fullmatch(r"0x[0-9a-f]*", raw):
        raise ValueError("Calldata must be hexadecimal (0-9, a-f).")
    if len(raw) % 2:
        raise ValueError("Calldata has an odd number of hex digits.")
    return raw


def word(raw, i):
    w = raw[10 + 64 * i: 10 + 64 * (i + 1)]
    return int(w, 16) if len(w) == 64 else None


def addr(raw, i):
    w = raw[10 + 64 * i: 10 + 64 * (i + 1)]
    return "0x" + w[-40:] if len(w) == 64 else None


def short(a):
    return f"{a[:6]}...{a[-4:]}" if a else "an unknown address"


def amount_text(v):
    if v is None:
        return "an unreadable amount"
    return "UNLIMITED" if v >= UNLIMITED else f"{v:,} raw token units"


def _result(category, risk, title, explanation, reasons, selector, **details):
    return {"category": category, "risk": risk, "title": title, "explanation": explanation,
            "reasons": reasons, "selector": selector, "details": details}


# ---- main analysis ---------------------------------------------------------------------------
def analyze(calldata, value_eth=0.0, to=None):
    raw = clean_hex(calldata)
    value = float(value_eth or 0)
    sel = raw[:10] if len(raw) >= 10 else "0x"
    contract = f" on contract {short(to)}" if to else ""

    # plain ETH send / empty calldata
    if len(raw) < 10:
        if value > 0:
            return _result("Plain ETH transfer", "LOW", "Plain ETH transfer",
                           f"This sends {value} ETH to {short(to)}. No contract function is called. "
                           "Check the FULL recipient address, not only its first and last characters.",
                           ["No calldata", f"{value} ETH attached"], sel)
        return _result("Empty transaction", "LOW", "Empty transaction",
                       "No function call and no ETH. A zero-value empty transaction can be used to plant a "
                       "fake entry in a wallet history, but it moves no funds.", ["No calldata, 0 ETH"], sel)

    # ---- allowance grants (ice phishing) ----
    if sel in (APPROVE, INCREASE):
        spender, amt = addr(raw, 0), word(raw, 1)
        name = "approve" if sel == APPROVE else "increaseAllowance"
        if amt == 0:
            return _result("Allowance revoke", "LOW", "Revoking a token allowance",
                           f"This sets the allowance of {short(spender)} to zero{contract}. This protects you.",
                           ["Amount is 0 (revoke)"], sel, spender=spender)
        unl = amt is not None and amt >= UNLIMITED
        risk = "CRITICAL" if unl else "HIGH"
        reasons = [f"{name}() grants spending rights", "Amount is unlimited" if unl else "Fixed amount"]
        if value > 0:
            risk, reasons = "CRITICAL", reasons + [f"Also sends {value} ETH (an approval should not need ETH)"]
        return _result("Ice phishing risk", risk, "Token spending permission",
                       f"You are letting {short(spender)} spend {amount_text(amt)} of your tokens{contract}. "
                       "They can move these tokens at any time without asking you again. Sign only if this is a "
                       "contract you trust (for example a known exchange), not a random wallet or an unknown site.",
                       reasons, sel, spender=spender, amount=amt, unlimited=unl)

    if sel == SET_ALL:
        op, flag = addr(raw, 0), word(raw, 1)
        if flag == 0:
            return _result("Allowance revoke", "LOW", "Revoking NFT collection access",
                           f"This removes {short(op)} as an operator of your NFTs{contract}. This protects you.",
                           ["setApprovalForAll(false)"], sel, operator=op)
        return _result("Ice phishing risk", "CRITICAL", "Full control of an NFT collection",
                       f"You are giving {short(op)} control over EVERY NFT you own in this collection{contract}. "
                       "Scammers use this to empty a wallet in one transaction. Do not sign unless you fully trust "
                       "this marketplace or contract.",
                       ["setApprovalForAll(true) covers the whole collection"], sel, operator=op)

    if sel == PERMIT:
        owner, spender, amt = addr(raw, 0), addr(raw, 1), word(raw, 2)
        unl = amt is not None and amt >= UNLIMITED
        return _result("Ice phishing risk", "CRITICAL" if unl else "HIGH", "Gasless spending permission (permit)",
                       f"This submits a signed permit that lets {short(spender)} spend {amount_text(amt)} of "
                       f"{short(owner)}'s tokens. Permits need no approval transaction, so scammers like them: "
                       "one signature is enough to drain the tokens.",
                       ["permit() uses an off-chain signature", "Amount is unlimited" if unl else "Fixed amount"],
                       sel, owner=owner, spender=spender, amount=amt)

    if sel in PERMIT2:
        return _result("Ice phishing risk", "CRITICAL", f"{PERMIT2[sel]}",
                       "Permit2 can authorise another address to move your tokens through a signature. Only "
                       "continue if you started this action on a site you trust.", ["Permit2 spending authority"], sel)

    # ---- transfers (address poisoning / drains) ----
    if sel == TRANSFER:
        to_addr, amt = addr(raw, 0), word(raw, 1)
        if amt == 0:
            return _result("Address poisoning", "HIGH", "Zero-value token transfer",
                           f"This transfers 0 tokens to {short(to_addr)}. No money moves, but it leaves a fake entry "
                           "in a wallet history so a lookalike address can be copied by mistake later. Never copy an "
                           "address from your history without comparing every character.",
                           ["transfer() with amount 0"], sel, to=to_addr)
        risk = "MODERATE"
        return _result("Token transfer", risk, "Token transfer",
                       f"This sends {amount_text(amt)} to {short(to_addr)}{contract}. Check the FULL recipient "
                       "address character by character: lookalike addresses are the address-poisoning trick.",
                       ["Ordinary transfer, recipient needs checking"], sel, to=to_addr, amount=amt)

    if sel in (TRANSFER_FROM, SAFE_TRANSFER_FROM):
        frm, to_addr, amt = addr(raw, 0), addr(raw, 1), word(raw, 2)
        if sel == TRANSFER_FROM and amt == 0:
            return _result("Address poisoning", "HIGH", "Zero-value transferFrom",
                           f"This 'moves' 0 tokens from {short(frm)} to {short(to_addr)}. Nothing is taken, but it "
                           "plants a fake transfer record in the history of the sender.",
                           ["transferFrom() with amount 0"], sel, sender=frm, to=to_addr)
        return _result("Ice phishing risk", "HIGH", "Pulling tokens or an NFT from an address",
                       f"This moves {'an NFT or token id' if sel == SAFE_TRANSFER_FROM else amount_text(amt)} from "
                       f"{short(frm)} to {short(to_addr)}. Normally only a trusted app uses an allowance like this. "
                       "If a website asks YOU to sign it and you do not know why, it is likely a drain.",
                       ["transferFrom-type call: spends an existing allowance"], sel, sender=frm, to=to_addr)

    # ---- NFT marketplace orders ----
    if sel in NFT_ORDERS:
        return _result("NFT order scam risk", "HIGH", f"NFT marketplace order ({NFT_ORDERS[sel]})",
                       "This executes a marketplace order. Scam orders set the price to 0 or the fee to 100% and "
                       "name the scammer as recipient, so your NFT leaves for nothing. Compare the price shown here "
                       "with what you expect to receive.", ["Marketplace order fulfilment"], sel)

    # ---- bundled calls ----
    if sel in MULTICALL:
        embedded = [s for s in EMBED_APPROVALS if s in raw[10:]]
        if embedded:
            return _result("Ice phishing risk", "HIGH", "Bundled actions that include an approval",
                           "This bundles several actions into one transaction and one of them appears to grant a "
                           "token or NFT permission. Bundles hide what is really happening.",
                           ["multicall / router with an embedded approval"], sel)
        return _result("Bundled call", "MODERATE", "Bundled actions",
                       "This bundles several actions into one transaction. They cannot be fully read from the data "
                       "alone. Only continue if you started this on a site you trust.",
                       ["multicall / router"], sel)

    # ---- payable function traps ----
    if sel in PAYABLE_TRAPS and value > 0:
        return _result("Payable function scam risk", "HIGH", f"'{PAYABLE_TRAPS[sel]}' function that takes your ETH",
                       f"You are sending {value} ETH to a function named '{PAYABLE_TRAPS[sel]}'{contract}. Scam "
                       "contracts use names like claim, SecurityUpdate or ConnectWallet to look harmless while "
                       "keeping the ETH.", [f"Known scam-style name: {PAYABLE_TRAPS[sel]}", f"{value} ETH attached"],
                       sel)
    if value > 0:
        return _result("Payable function risk", "HIGH", "Unrecognised function that takes ETH",
                       f"You are sending {value} ETH to a function this tool does not recognise{contract}. Payable "
                       "functions with unclear names are the typical 'airdrop' or 'claim' trap.",
                       ["Unknown selector", f"{value} ETH attached"], sel)
    return _result("Unrecognised call", "MODERATE", "Unrecognised function",
                   "This tool does not recognise this function and no ETH is attached. That does not mean it is "
                   "safe: check the website and the contract before signing.", ["Unknown selector"], sel)


# ---- lookalike address check ----------------------------------------------------------------
def _norm(a):
    a = (a or "").strip().lower()
    if not re.fullmatch(r"0x[0-9a-f]{40}", a):
        raise ValueError("An Ethereum address is 0x followed by 40 hex characters.")
    return a


def lookalike(addr_a, addr_b, n=4):
    """Paper rule: first n and last n hex characters equal => displays identically in many wallets."""
    a, b = _norm(addr_a), _norm(addr_b)
    if a == b:
        return {"same_address": True, "lookalike": False, "verdict": "These are the SAME address.",
                "diff_positions": []}
    pre, suf = a[2:2 + n] == b[2:2 + n], a[-n:] == b[-n:]
    diffs = [i for i in range(2, 42) if a[i] != b[i]]
    risky = pre and suf
    verdict = ("WARNING: different addresses with the same start and end. Wallets that shorten addresses show "
               "them identically. This is the address-poisoning trick." if risky else
               "Different addresses. They do not share both the first and last characters.")
    return {"same_address": False, "lookalike": risky, "prefix_match": pre, "suffix_match": suf,
            "verdict": verdict, "diff_positions": diffs, "a": a, "b": b, "n": n}


def render_lookalike_markdown(res):
    """Marks differing characters in bold so the middle part stands out."""
    if res.get("same_address") or "a" not in res:
        return ""
    def mark(s):
        return "0x" + "".join(f"**{c}**" if i in res["diff_positions"] else c for i, c in enumerate(s) if i >= 2)
    return f"A: `{res['a']}`  \nB: `{res['b']}`  \nDifferent characters (bold) in A: {mark(res['a'])}"


def format_report(res):
    lines = [f"[{res['risk']}] {res['title']}", res["explanation"], "", "Why: " + "; ".join(res["reasons"]),
             f"Selector: {res['selector']}"]
    return "\n".join(lines)


if __name__ == "__main__":
    demo = "0x095ea7b3" + "ab" * 20 and "0x095ea7b3" + ("0" * 24 + "ab" * 20) + "f" * 64
    print(format_report(analyze(demo, 0, "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48")))