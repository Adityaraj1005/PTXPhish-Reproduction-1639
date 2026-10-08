"""
attacker_simulator.py
Deconstructs malicious transactions to simulate and explain how 
scammers construct EVM payload-based phishing attacks.
"""

def simulate_attack_anatomy(selector: str, calldata: str, value_eth: float, category: str):
    """
    Generates a step-by-step technical breakdown of how the scam payload 
    was constructed by an attacker based on its signature and category.
    """
    anatomy = {
        "selector": selector,
        "category": category,
        "attacker_tactic": "",
        "payload_breakdown": [],
        "victim_risk": ""
    }
    
    # Clean selector format
    sel_lower = selector.lower()
    
    if "nft" in category.lower() or sel_lower in ["0x1255f005", "0xfb0f3ee1", "0x539564c7"]:
        anatomy["attacker_tactic"] = "Off-Chain Marketplace Signature / Permit2 Order Hijacking"
        anatomy["payload_breakdown"] = [
            "1. Encoded a low-value or zero-value consideration (<= 0.005 ETH) to bypass standard high-value alerts.",
            "2. Bundled malicious Permit2 signature allowances allowing a third-party operator to drain floor-price NFTs.",
            "3. Used proxy routing to obscure the final destination of the transferred assets."
        ]
        anatomy["victim_risk"] = "Critical: Complete loss of approved NFT collections without native token movement."

    elif "poison" in category.lower() or sel_lower in ["0xa9059cbb", "0x23b872dd"]:
        anatomy["attacker_tactic"] = "Address Poisoning / Zero-Value Transfer Injection"
        anatomy["payload_breakdown"] = [
            "1. Generated a vanity address matching the prefix/suffix of the victim's frequent contact.",
            "2. Dispatched a 0 ETH transfer (or dust transfer) directly into the victim's transaction history logs.",
            "3. Relies on human error where copy-pasting addresses from recent history targets the attacker's twin wallet."
        ]
        anatomy["victim_risk"] = "High: Accidental future asset transfers sent directly to the attacker's lookalike address."

    elif "ice" in category.lower() or sel_lower in ["0x095ea7b3", "0xa22cb465", "0x39509351"]:
        anatomy["attacker_tactic"] = "Ice Phishing / Token Allowance Expropriation"
        anatomy["payload_breakdown"] = [
            "1. Disguised a malicious `approve` or `setApprovalForAll` call inside a fake 'Claim Airdrop' or 'Governance Vote' DApp interface.",
            "2. Requested unlimited token spending allowance (Max Uint256) directed to an unverified drainer contract.",
            "3. Allowed the scammer to silently execute `transferFrom` later at their convenience."
        ]
        anatomy["victim_risk"] = "Critical: Silent, delayed emptying of all ERC-20 token balances in the victim's wallet."

    else:
        anatomy["attacker_tactic"] = "Payable Function Abuse / Interactive Contract Trap"
        anatomy["payload_breakdown"] = [
            "1. Wrapped malicious transfer logic inside unverified fallback or receive functions.",
            "2. Triggered native ETH transfers disguised as transaction gas refunds or bridge fees.",
            "3. Intercepted state variables during execution to redirect incoming value."
        ]
        anatomy["victim_risk"] = "Moderate to High: Direct theft of attached native ETH or contract state manipulation."

    return anatomy