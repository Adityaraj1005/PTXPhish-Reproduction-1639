# PTXPhish: Reproduction Study

**Course Project / Paper Reproduction**  
**Student ID:** 2024UCP1639  

---

## 📌 Project Overview
This repository contains our work to reproduce the research paper from **NDSS 2025**:
> **Dissecting Payload-based Transaction Phishing on Ethereum**  
> *Authors:* Zhuo Chen, Yufeng Hu, Bowen He, Dong Luo, Lei Wu, Yajin Zhou  

---

## 🔗 Important Links
- **Research Paper (PDF):** [Read Paper Here](https://www.ndss-symposium.org/wp-content/uploads/2025-311-paper.pdf)
- **Original Code & Dataset:** [GitHub Repository](https://github.com/blocksecteam/PTXPhish)

---

## 💡 What is This Project About? (Super Simple Explanation)
If you know nothing about blockchain, think of this like catching online credit card scams, but for crypto wallets:
- **The Problem:** Scammers can't steal your crypto directly without your permission. Instead, they trick you into clicking "Confirm" on a fake transaction (like a fake free gift or reward). The hidden code inside the transaction secretly gives the scammer permission to drain your digital wallet.
- **The Solution (PTXPhish):** The researchers built a smart tool that looks inside these transaction codes before they happen to spot the scam and block it.
- **Our Job:** We are downloading their code and data to re-run their tests and see if we get the exact same results they published.

---

## 📊 Dataset Description
We have saved two main files inside our `dataset/` folder:
1. **`PTXPHISH.xlsx`**: A spreadsheet containing thousands of real-world scam transactions and normal transactions. We use this as our test sheet.
2. **`InitialAddress.xlsx`**: A list of known scammer wallet addresses that the researchers used as a starting point to find the scams.

---

## 🛠️ Step-by-Step Plan (What We Have to Do)
Here are the simple steps we will follow to complete our assignment:

* **Step 1: Explore the Data**  
  Look inside `PTXPHISH.xlsx` to understand how the scam transactions are organized.
* **Step 2: Set Up the Code**  
  Install the necessary programming environment and tools.
* **Step 3: Run the Tests**  
  Run the detection scripts over the dataset to see how well the tool catches scams.
* **Step 4: Match the Results**  
  Check if our accuracy numbers match what the authors wrote in their research paper.
* **Step 5: Final Report**  
  Clean up our repository and submit our findings.

---

## 📑 Research Paper Breakdown (Made Simple)

### 1. What is the Paper About?
Traditional phishing steals passwords or login keys. This paper studies a new scam called **PTXPHISH (Payload-based Transaction Phishing)**. 
Instead of stealing passwords, scammers create tricky transaction codes and get victims to sign them directly inside their crypto wallet (like MetaMask). The wallet then follows the code and gives the scammer the victim's money.

### 2. The 4 Main Attack Tricks
The authors analyzed 5,000 confirmed scams and grouped them into 4 common tricks:
* **Ice Phishing:** Tricking users into signing an `approve` or `permit` button (like signing a blank check) under the disguise of a "free airdrop," giving the scammer full permission to steal funds later.
* **NFT Order Abuse:** Tricking users into signing an offer that sells their expensive NFT for almost $0.
* **Address Poisoning:** Sending fake $0 transactions to a user from a lookalike wallet address, hoping the user will accidentally copy-paste the scammer's address next time.
* **Payable Function Abuse:** Tricking the user into clicking a button that directly sends real Ethereum coins straight into the scammer's wallet.

### 3. How the Tool (PTXPhish) Catches Them
* Standard antivirus tools only check website blacklists, which fail when scammers create fresh websites every day.
* **PTXPhish runs a private test first:** It simulates the transaction before it is confirmed to see what actually happens.
* It checks the money flow: If money or spending permission leaves the user's wallet and nothing fair comes back, it blocks the transaction.
* It achieved over **99% accuracy** and inspects a whole block in just **390 ms**.

### 4. What the Researchers Found in Real Life
* The team monitored Ethereum live for **300 days**.
* Found **130,637 scam transactions** that stole over **$341.9 million**.
* Helped real victims by sending **2,539 warning alerts** and reporting **1,726 scammer addresses** to security blacklists.


---

## 🛠️ Project Setup & Data Engineering Pipeline

This repository reproduces the research benchmark and evaluation framework introduced in the NDSS 2025 paper **PTXPhish**. Below is the end-to-end breakdown of how our environment is configured, dependencies are managed, and how the raw benchmark data was inspected and transformed into a clean training/evaluation pipeline.

---

### 1. Environment & Dependencies (`requirements.txt`)

To ensure reproducibility across different operating systems without contaminating global system Python packages, all development is executed inside an isolated virtual environment (`venv`). 

Key dependencies tracked in `requirements.txt`:
* **`web3`**: Interfaces directly with Ethereum JSON-RPC nodes to fetch low-level transaction payloads, receipt receipts, and state execution traces.
* **`pandas`**: High-performance data manipulation used to parse the multi-level dataset matrices and output flattened tabular structures.
* **`openpyxl`**: Underlying engine allowing Pandas to parse modern `.xlsx` workbooks containing complex merged cells.
* **`requests`**: Handles HTTP requests to blockchain explorers (Etherscan API) and external RPC endpoints.
* **`matplotlib` & `seaborn`**: Generates visual representations of attack distribution frequencies, inspection latencies, and detection confusion matrices.

#### Installation
```bash
# 1. Activate your local virtual environment:
# On Windows PowerShell:
.\venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# 2. Install all pinned dependencies:
pip install -r requirements.txt


### 2. Checking the Raw Data (`scripts/eda_dataset.py`)
* **Why we need it**: The original file (`PTXPHISH.xlsx`) has messy merged headers and 28 separate columns, making it hard to read.
* **What it does**:
  * Reads the top header rows to find the scam names.
  * Counts how many transactions are in each group.
  * Makes sure the transaction IDs are valid and not broken.

---

### 3. Cleaning the Data (`scripts/clean_dataset.py`)
* **Why we need it**: Merged Excel cells leave lots of empty blank spaces. This script fixes them and makes a simple table.
* **What it does**:
  * Fills in missing column labels so no scam type is lost.
  * Cleans and checks all 18,556 transaction IDs.
  * Saves everything into a neat CSV file: `dataset/cleaned_ptxphish.csv`.

---

### 📊 Dataset Summary

| Scam Type | Total Count | Simple Meaning |
| :--- | :---: | :--- |
| **Ice Phishing** | **2,569** | Tricks users into giving permission to steal tokens |
| **NFT Order Scam** | **609** | Tricks users into giving away costly NFTs for free |
| **Address Poisoning** | **226** | Sends fake 0-value transfers from lookalike addresses |
| **Payable Function Scam** | **15,152** | Tricks users into sending real ETH directly to the scammer |
| **Total Valid Transactions** | **18,556** | Clean data ready for building detection rules |


---

### 4. Blockchain Connection & Verification (`scripts/test_rpc.py`)
* **Purpose**: Tests our direct link to the Ethereum network and proves we can pull real scam records using IDs from our cleaned dataset.
* **What it does**:
  * Uses a list of free public Ethereum nodes (with automatic fallback) to prevent rate-limiting or crashes.
  * Grabs a sample Ice Phishing transaction ID from `cleaned_ptxphish.csv`.
  * Queries the blockchain to retrieve live details: the victim wallet, the target contract, value sent, and the function bytecode.