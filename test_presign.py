"""Offline tests. Run:  python test_presign.py   (or pytest)"""
import presign as p

pad = lambda a: "0" * 24 + a[2:]
SPENDER = "0x" + "ab" * 20
OTHER = "0x" + "cd" * 20
UNL, ONE, ZERO = "f" * 64, "0" * 63 + "1", "0" * 64


def test_unlimited_approve():
    r = p.analyze("0x095ea7b3" + pad(SPENDER) + UNL)
    assert r["risk"] == "CRITICAL" and r["details"]["unlimited"] and "UNLIMITED" in r["explanation"]

def test_limited_approve():
    assert p.analyze("0x095ea7b3" + pad(SPENDER) + ONE)["risk"] == "HIGH"

def test_revoke_is_low():
    assert p.analyze("0x095ea7b3" + pad(SPENDER) + ZERO)["risk"] == "LOW"

def test_approve_with_eth_is_critical():
    assert p.analyze("0x095ea7b3" + pad(SPENDER) + ONE, 0.5)["risk"] == "CRITICAL"

def test_set_approval_for_all():
    assert p.analyze("0xa22cb465" + pad(SPENDER) + ONE)["risk"] == "CRITICAL"
    assert p.analyze("0xa22cb465" + pad(SPENDER) + ZERO)["risk"] == "LOW"

def test_zero_transfer_is_poisoning():
    r = p.analyze("0xa9059cbb" + pad(SPENDER) + ZERO)
    assert r["category"] == "Address poisoning" and r["risk"] == "HIGH"

def test_normal_transfer():
    assert p.analyze("0xa9059cbb" + pad(SPENDER) + ONE)["risk"] == "MODERATE"

def test_zero_transferfrom_is_poisoning():
    r = p.analyze("0x23b872dd" + pad(SPENDER) + pad(OTHER) + ZERO)
    assert r["category"] == "Address poisoning"

def test_nft_order():
    assert p.analyze("0xfb0f3ee1" + "00" * 64)["category"] == "NFT order scam risk"

def test_multicall_with_embedded_approval():
    data = "0xac9650d8" + "00" * 8 + "095ea7b3" + "00" * 40
    assert p.analyze(data)["risk"] == "HIGH"

def test_payable_trap_and_unknown():
    assert p.analyze("0x4e71d92d", 0.1)["risk"] == "HIGH"
    assert p.analyze("0xdeadbeef", 0.1)["category"] == "Payable function risk"
    assert p.analyze("0xdeadbeef", 0)["risk"] == "MODERATE"

def test_empty_calldata():
    assert p.analyze("0x", 1.0)["risk"] == "LOW"
    assert p.analyze("", 0)["risk"] == "LOW"

def test_bad_input():
    for bad in ("0xzz", "0x123"):
        try:
            p.analyze(bad); assert False
        except ValueError:
            pass

def test_lookalike():
    a = "0xa7B4BAC8f0f9692e56750aEFB5f6cB5516E90570"
    b = "0xa7b4" + "1" * 32 + "0570"                      # same first 4 and last 4 characters
    r = p.lookalike(a, b)
    assert r["lookalike"] and r["prefix_match"] and r["suffix_match"]
    assert not p.lookalike(a, "0x" + "11" * 20)["lookalike"]
    assert p.lookalike(a, a.lower())["same_address"]
    # pair quoted in the paper: shares the first 3 and last 4 characters, so use n=3
    paper_fake = "0xa7Bf48749D2E4aA29e3209879956b9bAa9E90570"
    assert p.lookalike(a, paper_fake, n=3)["lookalike"] and not p.lookalike(a, paper_fake, n=4)["lookalike"]
    try:
        p.lookalike("0x123", a); assert False
    except ValueError:
        pass


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t(); print("ok  ", t.__name__)
    print(f"\n{len(tests)} tests passed")