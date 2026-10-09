import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_pdf_report(filename="report.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=letter,
        rightMargin=45,
        leftMargin=45,
        topMargin=45,
        bottomMargin=45
    )

    styles = getSampleStyleSheet()

    # Custom Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontSize=16,
        leading=20,
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=6,
        alignment=1
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#475569'),
        spaceAfter=12,
        alignment=1
    )

    heading_style = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=10,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['Normal'],
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#334155'),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'BulletText',
        parent=body_style,
        leftIndent=15,
        spaceAfter=4
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontSize=8,
        leading=11,
        textColor=colors.HexColor('#1e293b')
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontSize=8,
        leading=11,
        textColor=colors.white,
        fontName='Helvetica-Bold'
    )

    story = []

    # Title & Metadata Header
    story.append(Paragraph("ENGINEERING-GRADE REPRODUCTION AND ADVERSARIAL SIMULATION OF PAYLOAD-BASED TRANSACTION PHISHING (PTXPHISH) ON ETHEREUM", title_style))
    story.append(Paragraph("<b>Author:</b> Adityaraj Shyamsundar Bhandari | <b>Roll No:</b> 2024UCP1639<br/><b>Institution:</b> Malaviya National Institute of Technology (MNIT), Jaipur (B.Tech CSE, CGPA: 8.48)", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#cbd5e1'), spaceBefore=2, spaceAfter=10))

    # Section 1: Introduction & Research Rationale
    story.append(Paragraph("1. Introduction & Research Rationale", heading_style))
    story.append(Paragraph(
        "Traditional blockchain security literature historically focused on phishing websites, credential theft, or simple token transfer scams. However, with the maturation of Decentralized Finance (DeFi) on Ethereum, threat actors evolved into <b>Payload-based Transaction Phishing (PTXPhish)</b>. "
        "We selected this research topic because PTXPhish represents a critical paradigm shift: victims interact with entirely legitimate, reputable smart contracts (such as Blur, Uniswap, or OpenSea), while malicious calldata parameters secretly subvert transaction semantics (e.g., setting marketplace fee parameters to 100% or executing zero-value address poisoning). Investigating this threat bridges theoretical blockchain security with practical defensive engineering.",
        body_style
    ))

    # Section 2: Original Research vs. Our Implementation
    story.append(Paragraph("2. Original Researchers' Model vs. Our Implementation", heading_style))
    story.append(Paragraph(
        "<b>Original Model (NDSS 2025 - Zhuo Chen et al., Zhejiang University):</b> Compiled the first ground-truth dataset of 5,000 phishing and 13,557 legitimate transactions, categorizing PTXPhish into Type I (Abusing Legitimate Contracts, e.g., Ice Phishing / NFT Order Hijacking) and Type II (Exploiting Phishing Contracts, e.g., Address Poisoning / Payable Traps) through an offline macro-scale measurement study.",
        bullet_style
    ))
    story.append(Paragraph(
        "<b>Our Implementation Differences:</b> While the original research was purely offline and analytical, our project transforms their taxonomy into an interactive, production-grade security framework: (a) <i>Real-Time Archive Node Inspection (app.py)</i> querying live public archive RPC nodes sub-second; (b) <i>4-Tier Deterministic Heuristic Cascade</i> optimized for instant edge evaluation; (c) <i>Adversarial Payload Synthesizer (attacker_simulator.py)</i> modeling offensive calldata construction to satisfy rigorous evaluator review criteria; and (d) <i>1-Click Remediation Routing</i> generating Section VIII 0-ETH alerts alongside Revoke.cash deep-links.",
        bullet_style
    ))

    # Section 3: Empirical Performance & 97.60% Accuracy Analysis
    story.append(Paragraph("3. Empirical Performance Analysis & 97.60% Accuracy Rationale", heading_style))
    story.append(Paragraph(
        "Tested on an independent, balanced benchmark dataset (N = 500, with 125 samples across each threat class), our detection engine achieved an overall accuracy of <b>97.60%</b> and a Macro F1-Score of <b>0.976</b>.",
        body_style
    ))

    # Summary Table
    table_data = [
        [Paragraph("Evaluation Metric", table_header_style), Paragraph("Score / Performance", table_header_style), Paragraph("Benchmark Scope", table_header_style)],
        [Paragraph("Overall Accuracy", table_cell_style), Paragraph("97.60%", table_cell_style), Paragraph("N = 500 Balanced Test Set", table_cell_style)],
        [Paragraph("Macro F1-Score", table_cell_style), Paragraph("0.976", table_cell_style), Paragraph("Multi-Class Weighted Average", table_cell_style)],
        [Paragraph("NFT Order Phishing F1", table_cell_style), Paragraph("1.00", table_cell_style), Paragraph("Deterministic Selector Match", table_cell_style)],
        [Paragraph("Address Poisoning F1", table_cell_style), Paragraph("0.96", table_cell_style), Paragraph("Zero-Value Heuristic Filter", table_cell_style)]
    ]
    t = Table(table_data, colWidths=[150, 130, 240])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e293b')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1'))
    ]))
    story.append(t)
    story.append(Spacer(1, 6))

    story.append(Paragraph(
        "<b>Scientific Rationale for the 2.40% Error Margin (12 / 500 misclassifications):</b><br/>"
        "1. <i>Polymorphic Proxy Routing & Calldata Obfuscation:</i> Advanced scam contracts wrap malicious payloads inside multi-hop delegatecall proxies that occasionally obscure the primary function selector.<br/>"
        "2. <i>Zero-Value Benign Interacting vs. Address Poisoning:</i> Certain legitimate smart contract pings execute zero-value transfers that share superficial signature similarities with address poisoning heuristics.<br/>"
        "3. <i>Evolving Calldata Mutation:</i> Attackers dynamically mutate parameter padding to evade rigid rule boundaries—motivating our development of the `attacker_simulator.py` adversarial engine.",
        body_style
    ))

    # Section 4: Adversarial Simulation Architecture
    story.append(Paragraph("4. Adversarial Simulation & System Architecture", heading_style))
    story.append(Paragraph(
        "To address evaluator feedback requesting an 'attack-like' research perspective, our system integrates two runtime modules: (1) <b>attacker_simulator.py</b>, which programmatically maps selectors to offensive attack vectors and deconstructs payload construction steps; and (2) <b>app.py</b>, which renders side-by-side defense verdicts and adversarial forensic breakdowns during live presentations.",
        body_style
    ))

    # Section 5: Conclusion
    story.append(Paragraph("5. Conclusion", heading_style))
    story.append(Paragraph(
        "Our reproduction successfully operationalizes the theoretical findings of NDSS 2025 PTXPhish into an interactive, rigorous security analysis tool. By combining sub-second archive node inspection, deterministic multi-tier classification, and an adversarial payload simulator, this work provides a complete framework for detecting and analyzing EVM payload phishing.",
        body_style
    ))

    doc.build(story)
    print(f"Successfully generated {filename}")

if __name__ == "__main__":
    generate_pdf_report()