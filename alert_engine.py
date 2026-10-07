"""
alert_engine.py
Implementation of the "Last Line" of PTXPhish (NDSS 2025):
"Additionally, we sent 2,539 on-chain alert messages, 
providing assistance to 1,980 victims of phishing attacks."
"""

from typing import Dict, Any

def encode_alert_calldata(message: str) -> str:
    """
    Encodes a human-readable security warning string into hex UTF-8 calldata
    so it can be permanently carried inside a 0-ETH alert transaction.
    """
    hex_payload = message.encode("utf-8").hex()
    return f"0x{hex_payload}"


def generate_rescue_transaction(
    victim_address: str, 
    threat_category: str, 
    attacker_address: str = "0xUnknown"
) -> Dict[str, Any]:
    """
    Crafts the simulated on-chain rescue transaction and remediation instructions.
    """
    # 1. Tailor warning messages by detected threat type
    threat_advisories = {
        "Ice Phishing": (
            f"[PTXPHISH RESCUE ALERT] High-risk approval detected for spender {attacker_address[:10]}... "
            f"Revoke immediately at https://revoke.cash/{victim_address}"
        ),
        "NFT Order Scam": (
            f"[PTXPHISH RESCUE ALERT] Exploitative marketplace order detected! "
            f"Cancel all unfulfilled Seaport listings immediately."
        ),
        "Address Poisoning": (
            f"[PTXPHISH RESCUE ALERT] Poisoning transfer detected! "
            f"Do not copy addresses from your recent transaction history."
        ),
        "Payable Function Scam": (
            f"[PTXPHISH RESCUE ALERT] Suspicious payable contract drained ETH! "
            f"Do not interact further with {attacker_address[:10]}..."
        )
    }

    advisory_text = threat_advisories.get(
        threat_category, 
        f"[PTXPHISH RESCUE ALERT] Suspicious payload detected targeting {victim_address}."
    )

    # 2. Encode to raw Ethereum transaction calldata
    alert_calldata = encode_alert_calldata(advisory_text)

    # 3. Assemble the raw 0-ETH rescue transaction structure
    rescue_tx = {
        "to": victim_address,
        "value": 0,                      # 0 ETH transaction
        "gasLimit": 25000,               # Base 21,000 + calldata gas
        "input": alert_calldata,         # Warning message encoded as calldata
        "raw_message": advisory_text,
        "remediation_url": f"https://revoke.cash/address/{victim_address}",
        "etherscan_url": f"https://etherscan.io/address/{victim_address}"
    }

    return rescue_tx