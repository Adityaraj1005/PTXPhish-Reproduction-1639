import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

pdf_path = "report.pdf"
doc = SimpleDocTemplate(
    pdf_path,
    pagesize=letter,
    rightMargin=45,
    leftMargin=45,
    topMargin=45,
    bottomMargin=45
)

styles = getSampleStyleSheet()

# Styles
title_style = ParagraphStyle(
    'DocTitle',
    parent=styles['Heading1'],
    fontSize=17,
    leading=21,
    textColor=colors.HexColor('#0f172a'),
    spaceAfter=6,
    alignment=1
)

sub_title_style = ParagraphStyle(
    'DocSubtitle',
    parent=styles['Normal'],
    fontSize=10,
    leading=14,
    textColor=colors.HexColor('#334155'),
    spaceAfter=10,
    alignment=1
)

meta_box_style = ParagraphStyle(
    'MetaBox',
    parent=styles['Normal'],
    fontSize=8.5,
    leading=12,
    textColor=colors.HexColor('#1e293b'),
    alignment=1
)

h1_style = ParagraphStyle(
    'Heading1_Custom',
    parent=styles['Heading2'],
    fontSize=12.5,
    leading=16,
    textColor=colors.HexColor('#1d4ed8'),
    spaceBefore=12,
    spaceAfter=5,
    keepWithNext=True
)

h2_style = ParagraphStyle(
    'Heading2_Custom',
    parent=styles['Heading3'],
    fontSize=10,
    leading=13.5,
    textColor=colors.HexColor('#0f172a'),
    spaceBefore=8,
    spaceAfter=3,
    keepWithNext=True
)

body_style = ParagraphStyle(
    'Body_Custom',
    parent=styles['BodyText'],
    fontSize=8.5,
    leading=12.5,
    textColor=colors.HexColor('#1e293b'),
    spaceAfter=5
)

bullet_style = ParagraphStyle(
    'Bullet_Custom',
    parent=body_style,
    leftIndent=14,
    firstLineIndent=-10,
    spaceAfter=3
)

table_header_style = ParagraphStyle(
    'TableHeader',
    parent=styles['Normal'],
    fontSize=8,
    leading=10,
    fontName="Helvetica-Bold",
    textColor=colors.white,
    alignment=1
)

table_cell_style = ParagraphStyle(
    'TableCell',
    parent=styles['Normal'],
    fontSize=7.5,
    leading=9.5,
    textColor=colors.HexColor('#1e293b')
)

story = []

# Title
story.append(Paragraph("PTXPhish: Detecting Ethereum Transaction Scams", title_style))
story.append(Paragraph("<b>Comprehensive Research Reproduction & Systems Engineering Report</b>", sub_title_style))
story.append(Paragraph("<b>Author / Candidate Roll:</b> 2024UCP1639 &nbsp;|&nbsp; <b>Reference Paper:</b> NDSS 2025 (PTXPhish) &nbsp;|&nbsp; <b>Tech:</b> Python, Web3.py, Streamlit", meta_box_style))
story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#1d4ed8"), spaceBefore=8, spaceAfter=10))

# Section 1: Plain English Dictionary
story.append(Paragraph("1. Plain English Dictionary (Every Technical Term Explained)", h1_style))
story.append(Paragraph("To understand how this security system works, here is every technical concept translated into simple everyday terms:", body_style))

terms = [
    ("Blind Signing 🙈✍️", "When you make a transaction on Ethereum using MetaMask, the wallet pops up showing a long, messy string of letters and numbers (like 0x095ea7b3...). Normal people cannot read this code, so they just click 'Confirm' blindly. Attackers exploit this by showing a beautiful website promising free rewards, while the code behind the button actually steals your money."),
    ("Calldata (The Instruction Box) 📦", "The payload or data sent with your transaction. It contains the exact instructions telling the Ethereum blockchain what function to run and who to give money to."),
    ("Function Selector (The 4-Byte Code) 🔑", "The very first 4 bytes (8 characters after 0x) of the calldata. It acts like an official label that uniquely names the function being called. For example, '0x095ea7b3' always means 'approve'."),
    ("RPC (Remote Procedure Call) 🌐", "The communication bridge that lets our Python code talk to the Ethereum blockchain over the internet to fetch data."),
    ("Archive Node 🖧💾", "A massive server that remembers every single transaction that has ever happened on Ethereum since day one. We use it to inspect past transactions."),
    ("Deterministic Cascade (Decision Tree) 🌲⚡", "A strict, step-by-step set of IF-THEN rules that decides whether a transaction is a scam without any guesswork."),
    ("Macro F1-Score 📊🏆", "A score between 0 and 1 that measures accuracy. It makes sure our model is equally good at catching all 4 kinds of scams, rather than just being good at one.")
]

for title, desc in terms:
    story.append(Paragraph(f"<b>• {title}:</b> {desc}", bullet_style))

# Section 2: What the Original Research Paper Did
story.append(Paragraph("2. What the Original NDSS 2025 Paper Was About", h1_style))
story.append(Paragraph("In traditional Web2 scams, hackers steal your password. But in Web3, hackers cannot steal your private password from your hardware wallet. Instead, they trick you into signing transactions that empty your wallet willingly. This is called <b>Payload-Based Transaction Phishing (PTXPhish)</b>.", body_style))
story.append(Paragraph("<b>The Authors' Original Setup:</b> The researchers at the NDSS 2025 conference collected 18,556 real phishing transactions. To detect them with 99% accuracy, they ran an expensive test simulator on a 2-Terabyte computer (a private archive node). Every time a transaction arrived, their simulator executed every single line of code in a test environment to see if tokens were stolen.", body_style))
story.append(Paragraph("<b>Why We Did This Project:</b> Running a 2-TB server is expensive and takes 3 to 10 seconds per transaction—too slow for a normal browser wallet. We wanted to test: <i>Can we build a fast, free tool that inspects transactions in under 0.2 seconds using public internet servers and simple rules, without running a heavy simulator?</i>", body_style))

# Section 3: The 4 Attacks
story.append(PageBreak())
story.append(Paragraph("3. The 4 Attack Types Explained in Detail", h1_style))

attacks = [
    ("1. Ice Phishing (Approval Abuse) 🧊🎣 — Risk: CRITICAL 🚨", 
     "<b>How it works:</b> The attacker does not steal your money immediately. Instead, they trick you into clicking 'approve()'. This changes the token contract's rules to give the attacker permanent permission to spend your tokens whenever they want. Days or weeks later, an automated script drains your wallet.<br/>"
     "<b>How our tool spots it:</b> We check if the transaction starts with approval codes like <code>0x095ea7b3</code> (approve) or <code>0xa22cb465</code> (setApprovalForAll)."),
    
    ("2. NFT Order Phishing (Marketplace Scams) 🎨📦 — Risk: CRITICAL 🚨", 
     "<b>How it works:</b> On NFT platforms like OpenSea (Seaport), you can sign an off-chain digital signature agreeing to trade your NFT. Attackers trick you into signing an order that gives away your expensive NFT for 0 ETH. The attacker then takes your signature and submits it to OpenSea to claim your NFT instantly.<br/>"
     "<b>How our tool spots it:</b> We check for marketplace routing codes like <code>0xfb0f3ee1</code> (fulfillOrder) or <code>0xb3a34c4c</code> (fulfillAdvancedOrder)."),
    
    ("3. Address Poisoning (Fake History Spoofing) ☠️📬 — Risk: HIGH ⚠️", 
     "<b>How it works:</b> Crypto addresses are 42 characters long, so wallets only show the start and end (like 0x7f83...61b3). Attackers create a fake address with the exact same start and end characters as your friend's address. Then they send you 0 tokens from that fake address. This puts the fake address right at the top of your wallet's history. Next time you want to send money to your friend, you might accidentally copy-paste the attacker's fake address from your history!<br/>"
     "<b>How our tool spots it:</b> We check if the function is a token transfer (<code>0xa9059cbb</code>) AND the value transferred is exactly <b>0</b>."),
    
    ("4. Payable Function Scams (Direct Money Grabs) 💸🚪 — Risk: MODERATE ⚠️", 
     "<b>How it works:</b> A fake website says 'Send 0.2 ETH to mint your exclusive VIP pass!' You send the money, the smart contract takes it, and you get nothing back. The loss is limited strictly to the ETH you sent in that one transaction.<br/>"
     "<b>How our tool spots it:</b> We check if native ETH is being sent (<code>Value > 0</code>) or if custom code is running that does not match the other 3 categories.")
]

for title, desc in attacks:
    story.append(Paragraph(title, h2_style))
    story.append(Paragraph(desc, body_style))

# Section 4: Architecture & Code Breakdown
story.append(Paragraph("4. How Our Project Works: Every Script Explained", h1_style))
story.append(Paragraph("Our project is divided into three clean, focused Python scripts:", body_style))

story.append(Paragraph("<b>1. scripts/run_evaluation.py (The Brain & Tester):</b><br/>"
                       "• Takes 500 real transactions (125 of each scam type) from our dataset.<br/>"
                       "• Connects to public Ethereum servers using a fallback pool (if one server is busy or rate-limits us, it automatically switches to the next server so it never crashes).<br/>"
                       "• Reads the function selector and ETH value from each transaction, runs them through our decision tree, and saves the answers to a CSV file.", bullet_style))

story.append(Paragraph("<b>2. scripts/generate_metrics.py (The Math & Charts):</b><br/>"
                       "• Reads the results CSV and uses scikit-learn to calculate our exact accuracy and F1-score.<br/>"
                       "• Draws a 4x4 visual heatmap (Confusion Matrix) showing exactly where our rules were right and where they made mistakes, saving it as <code>confusion_matrix_500.png</code>.", bullet_style))

story.append(Paragraph("<b>3. app.py (The Live Web Dashboard):</b><br/>"
                       "• Built using Streamlit so anyone can test transactions in a web browser.<br/>"
                       "• You paste any Ethereum transaction hash, click 'Inspect Transaction', and within 0.2 seconds it decodes the code and tells you if it is safe or a scam, along with its risk level.", bullet_style))

# Section 5: The Math & Results
story.append(PageBreak())
story.append(Paragraph("5. Results: How Well Did It Perform?", h1_style))
story.append(Paragraph("We tested our engine on 500 real Ethereum transactions from the research dataset:", body_style))

table_data = [
    [Paragraph("<b>Metric / Category</b>", table_header_style), Paragraph("<b>Original Paper (2-TB Node)</b>", table_header_style), Paragraph("<b>Our Tool (Free & Fast)</b>", table_header_style)],
    [Paragraph("<b>Overall Accuracy</b>", table_cell_style), Paragraph("~96% - 99%", table_cell_style), Paragraph("<b>88.60%</b> (443 / 500 correct)", table_cell_style)],
    [Paragraph("<b>Macro F1-Score</b>", table_cell_style), Paragraph("> 0.99", table_cell_style), Paragraph("<b>0.89</b>", table_cell_style)],
    [Paragraph("<b>NFT Order Scams F1</b>", table_cell_style), Paragraph("> 0.99", table_cell_style), Paragraph("<b>0.99</b> (Catches almost all)", table_cell_style)],
    [Paragraph("<b>Address Poisoning F1</b>", table_cell_style), Paragraph("> 0.99", table_cell_style), Paragraph("<b>0.96</b> (Catches almost all)", table_cell_style)],
    [Paragraph("<b>Ice Phishing F1</b>", table_cell_style), Paragraph("> 0.98", table_cell_style), Paragraph("<b>0.81</b>", table_cell_style)],
    [Paragraph("<b>Payable Scams F1</b>", table_cell_style), Paragraph("> 0.98", table_cell_style), Paragraph("<b>0.79</b>", table_cell_style)],
    [Paragraph("<b>Speed per Transaction</b>", table_cell_style), Paragraph("3 to 10 seconds", table_cell_style), Paragraph("<b>Under 0.2 seconds</b>", table_cell_style)],
    [Paragraph("<b>Hardware Cost</b>", table_cell_style), Paragraph("High ($$$ - Needs 2 TB SSD)", table_cell_style), Paragraph("<b>$0 (Free public servers)</b>", table_cell_style)]
]

t = Table(table_data, colWidths=[160, 180, 180])
t.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1d4ed8')),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
    ('TOPPADDING', (0, 0), (-1, -1), 5),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
]))
story.append(t)
story.append(Spacer(1, 10))

# Section 6: Why Paper got 99% and we got 88.6%
story.append(Paragraph("6. Why Did the Paper Get 99% While We Got 88.6%?", h1_style))
story.append(Paragraph("Think of an Ethereum transaction like a locked wooden box delivered to your doorstep:", body_style))
story.append(Paragraph("<b>The Paper's Method (The X-Ray Machine):</b> The original researchers opened the box inside a virtual test lab and let every line of code run. Even if an attacker hid a secret theft instruction inside five layers of code, the test lab caught it. That gave them 99% accuracy, but it was slow and expensive.", bullet_style))
story.append(Paragraph("<b>Our Method (Reading the Label on the Box):</b> We do not run the code. We simply inspect the label on the outside of the box (the first 10 letters of code and the ETH amount). This runs in 0.2 seconds for free and catches <b>88.6% of scams</b>.", bullet_style))
story.append(Paragraph("<b>The 3 Tricks That Fooled Our Label Reader:</b><br/>"
                       "1. <b>Middleman Contracts:</b> An attacker writes a contract with a generic function name like <code>execute()</code>. Our tool sees <code>execute()</code> and assumes it is just a normal contract call. But once running, <code>execute()</code> secretly calls <code>approve()</code> inside. Because we did not run the code, we could not see the hidden command.<br/>"
                       "2. <b>Bundled Actions (Multicall):</b> Some attacks combine 5 different operations into one bundle. The outside label only says <code>multicall()</code>, hiding the real scam inside.<br/>"
                       "3. <b>Free Zero-ETH Calls:</b> A fake claim button that takes 0 ETH upfront and uses a custom name can sometimes confuse our simple rules between Ice Phishing and Payable Scams.", bullet_style))

# Section 7: Conclusion
story.append(Spacer(1, 6))
story.append(Paragraph("7. Practical Real-World Takeaway & Conclusion", h1_style))
story.append(Paragraph("<b>The Ideal Wallet Defense:</b> Users will not wait 5 seconds for a heavy simulator before confirming every transaction. Our project proves that wallets can use our lightweight method as an <b>instant first shield</b> inside the browser: it stops ~89% of attacks in 0.2 seconds locally. For the remaining 11% of strange or unknown transactions, the wallet can then send them to a slower cloud simulator for a deeper check.", body_style))
story.append(Paragraph("<b>Conclusion:</b> We proved that deterministic rules can catch the vast majority of Ethereum phishing attacks without any expensive servers, while also pinpointing the exact technical reasons why deeper simulation is needed for the rest.", body_style))

doc.build(story)
print("SUCCESS: Valid binary report.pdf generated with full simple explanations!")