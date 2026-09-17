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
