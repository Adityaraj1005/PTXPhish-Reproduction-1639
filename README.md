# PTXPhish: Reproduction Study

**Course Project / Paper Reproduction**  
**Student ID:** 2024UCP1639  

---

## 📌 Project Overview
This repository contains the reproduction study, environment setup, and experimental evaluation for the **NDSS 2025** research paper:
> **Dissecting Payload-based Transaction Phishing on Ethereum**  
> *Authors:* Zhuo Chen, Yufeng Hu, Bowen He, Dong Luo, Lei Wu, Yajin Zhou  
> *Conference:* Network and Distributed System Security (NDSS) Symposium 2025

---

## 🔗 Important Links
- **Research Paper (PDF):** [NDSS 2025 Paper](https://www.ndss-symposium.org/wp-content/uploads/2025-311-paper.pdf)
- **Original Source Code & Dataset:** [blocksecteam/PTXPhish on GitHub](https://github.com/blocksecteam/PTXPhish)

---

## 🎯 Objectives
1. Understand the taxonomy of payload-based transaction phishing on Ethereum.
2. Set up the analysis pipeline and environment locally.
3. Replay, trace, and inspect transaction payloads from the benchmark dataset.
4. Reproduce the detection metrics (Precision, Recall, F1-Score) reported in the paper.
5. Document differences, RPC execution bottlenecks, and reproduction outcomes.

---

## 📖 Detailed Explanation: What is this Project About?

### 1. The Core Problem: Payload-based Web3 Phishing
In the Ethereum ecosystem, users sign transactions directly via non-custodial wallets (such as MetaMask). Unlike traditional Web2 phishing—where scammers steal login credentials or credit card numbers—Web3 attackers do not need account passwords. Instead, they trick victims into **signing deceptive transactions** that authorize the drainage of crypto assets (ETH, ERC-20 tokens, or NFTs).

Existing Web3 defense mechanisms primarily rely on **static domain blacklists** or **malicious contract address lists**. These defenses fail because:
- Attackers frequently register disposable domain names and deploy fresh, unflagged smart contracts.
- The malicious behavior is embedded directly inside the transaction call data (**the payload**), which standard blacklists cannot inspect in advance.

### 2. Attack Taxonomy
The research paper identifies and categorizes payload-based phishing into distinct mechanisms:
- **Deceptive Approvals / Permits:** Exploiting ERC-20 `approve()` or ERC-2612 `permit()` calls to grant arbitrary spending allowances under the guise of free token mints or claim rewards.
- **Concealed Asset Transfers:** Concealing direct transfer calls (`transfer`, `transferFrom`, `safeTransferFrom`) behind proxy or multicall contract architectures.
- **Spoofed Trades & Counterfeit Swaps:** Simulating decentralized exchange (DEX) swaps where the victim relinquishes high-value tokens in exchange for valueless clone tokens.
- **State & Simulation Tampering:** Crafting transaction parameters that look harmless during basic wallet pre-execution simulations, but divert assets when actually mined on-chain.

### 3. The PTXPhish Detection Approach
Rather than relying on superficial domain reputation, **PTXPhish** inspects execution-level semantics:
- **Transaction Simulation & Trace Collection:** Replaying unconfirmed transactions in a sandbox environment to extract internal contract call traces and state changes.
- **Semantic Asset-Flow Analysis:** Tracking which accounts transfer assets, verifying whether the caller receives proportional economic value, and checking whether spending authorizations are granted to untrusted contracts.
- **Rule-based Classification:** Applying deterministic behavioral rules to distinguish legitimate decentralized application interactions from predatory phishing patterns.

### 4. Our Reproduction Plan
- **Environment Reproduction:** Configure the required Python runtime, trace parser dependencies, and local/remote Ethereum execution providers.
- **Benchmark Evaluation:** Run the detection rules on the ground-truth phishing transactions and benign baseline datasets provided in the repository.
- **Validation:** Measure True Positives (TP), False Positives (FP), and False Negatives (FN) to verify if the experimental Precision and Recall figures match the published NDSS 2025 results.


---

## 📊 Dataset Description & Structure

The repository includes the ground-truth benchmark files under the `dataset/` directory sourced from real-world Ethereum transactions.

### 1. `PTXPHISH.xlsx` (Ground-Truth Evaluation Dataset)
* **Description:** The primary benchmark dataset containing thousands of verified Ethereum transactions labeled by attack type and asset class.
* **Core Contents:**
  * **Transaction Hashes (`tx_hash`):** Unique on-chain Ethereum identifiers for both malicious phishing transactions and benign baseline transactions.
  * **Phishing Categories:**
    * **Ice Phishing (Deceptive Approvals):** Transactions tricking users into signing ERC-20 `approve` or ERC-2612 `permit` signatures.
    * **NFT Order Manipulation:** Tricking victims into signing off-market Seaport orders that list NFTs for negligible amounts.
    * **Address Poisoning:** Attackers injecting zero-value or dust transactions to pollute wallet transfer histories with spoofed lookalike addresses.
    * **Payable Function Exploits:** Disguised smart contract invocations (e.g., fake airdrop claims) that directly transfer native ETH to the attacker.
    * **Benign Baseline:** 13,000+ legitimate transactions used to test false-positive rates (FPR).
* **Role in Project:** Serves as the test ground truth for reproducing the detection rates, confusion matrix, precision, and recall metrics reported in NDSS 2025.

### 2. `InitialAddress.xlsx` (Seed Phishing Addresses)
* **Description:** The curated catalog of known attacker wallets and malicious smart contract addresses that served as the root seeds for the data collection pipeline.
* **Role in Project:**
  * Documents the origin points used to crawl and trace transaction flows on Ethereum.
  * Used to evaluate whether heuristic rules can detect zero-day phishing contracts versus previously flagged addresses.

| File Name | Primary Entity | Role / Usage in Reproduction |
| :--- | :--- | :--- |
| `PTXPHISH.xlsx` | Transaction Hashes (`tx_hash`) | Evaluating model detection, Precision, Recall, and F1-Score |
| `InitialAddress.xlsx` | Ethereum Addresses (`0x...`) | Seed tracking, provenance verification, and contract inspection |
