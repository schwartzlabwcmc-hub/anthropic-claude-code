#!/usr/bin/env python3
"""Generate a PDF report of spine surgery opioid prescribing analysis results."""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.colors import HexColor
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak, KeepTogether
)
from reportlab.lib import colors
import os

BASE = "/home/user/anthropic-claude-code"
OUTPUT = os.path.join(BASE, "spine_surgery_prescribing_report.pdf")

doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=letter,
    topMargin=0.75*inch,
    bottomMargin=0.75*inch,
    leftMargin=0.75*inch,
    rightMargin=0.75*inch,
)

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    'Title2', parent=styles['Title'], fontSize=20, spaceAfter=6,
    textColor=HexColor('#1a1a2e')
))
styles.add(ParagraphStyle(
    'Subtitle', parent=styles['Normal'], fontSize=12, alignment=TA_CENTER,
    spaceAfter=20, textColor=HexColor('#555555')
))
styles.add(ParagraphStyle(
    'SectionHead', parent=styles['Heading2'], fontSize=14, spaceBefore=16,
    spaceAfter=8, textColor=HexColor('#16213e')
))
styles.add(ParagraphStyle(
    'SubSectionHead', parent=styles['Heading3'], fontSize=12, spaceBefore=12,
    spaceAfter=6, textColor=HexColor('#1a1a2e')
))
styles.add(ParagraphStyle(
    'BodyText2', parent=styles['Normal'], fontSize=10, spaceAfter=6,
    leading=14
))
styles.add(ParagraphStyle(
    'BulletText', parent=styles['Normal'], fontSize=10, spaceAfter=4,
    leading=14, leftIndent=20, bulletIndent=10
))
styles.add(ParagraphStyle(
    'SmallNote', parent=styles['Normal'], fontSize=8, textColor=HexColor('#888888'),
    spaceAfter=4
))

TABLE_STYLE = TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), HexColor('#16213e')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTSIZE', (0, 0), (-1, -1), 8),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
    ('ALIGN', (0, 0), (0, -1), 'CENTER'),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#f0f0f0')]),
    ('TOPPADDING', (0, 0), (-1, -1), 3),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
])

elements = []

# ── Title Page ──
elements.append(Spacer(1, 1.5*inch))
elements.append(Paragraph(
    "Longitudinal Analysis of Multimodal Pain Management<br/>Prescribing Among Spine Surgeons",
    styles['Title2']
))
elements.append(Paragraph(
    "United States, 2014–2023<br/>Medicare Part B &amp; Part D Claims Data",
    styles['Subtitle']
))
elements.append(Spacer(1, 0.5*inch))
elements.append(Paragraph(
    "Data Source: Centers for Medicare &amp; Medicaid Services (CMS)<br/>"
    "Medicare Provider Utilization and Payment Data<br/>"
    "Accessed via CMS data.cms.gov API",
    styles['Subtitle']
))
elements.append(PageBreak())

# ── Key Findings ──
elements.append(Paragraph("Key Findings", styles['SectionHead']))
elements.append(Paragraph(
    "<b>Study Population:</b> 6,810 unique procedure-confirmed spine surgeons identified "
    "across 2014–2023 (neurosurgery + orthopedic surgery performing spine CPT codes). "
    "~4,198 spine surgeons per year in 2014 declining to ~3,925 in 2023. "
    "All 10 years of data (2014–2023) included.",
    styles['BodyText2']
))
elements.append(Spacer(1, 6))

findings = [
    ("<b>Opioid Prescribing (−51.7%, p&lt;0.001):</b> Total opioid claims fell from 707,906 (2014) to "
     "341,801 (2023). Claims per provider declined from 190.3 to 135.6 (−28.7%, p&lt;0.001). "
     "Average days supply per opioid claim decreased from 15.4 to 11.1 days (−28.3%, p&lt;0.001). "
     "Total opioid drug cost dropped from $18.8M to $4.4M (−76.8%, p&lt;0.001). "
     "Cost per opioid claim fell from $26.52 to $12.73 (−52.0%)."),
    ("<b>Gabapentinoid Prescribing (+39.3%, p&lt;0.001):</b> Total claims rose from 151,485 to 211,067. "
     "Claims per provider increased from 59.7 to 86.4 (+44.7%, p&lt;0.001). "
     "Despite volume increase, cost per claim fell from $40.58 to $15.10 (−62.8%) due to generic availability."),
    ("<b>Muscle Relaxant Prescribing (+59.3%, p&lt;0.001):</b> Total claims rose from 113,116 to 180,212. "
     "Claims per provider increased from 58.2 to 81.6 (+40.3%, p&lt;0.001). "
     "Cost per claim fell from $20.67 to $10.47 (−49.3%)."),
    ("<b>NSAID Prescribing (+22.8%, p&lt;0.05):</b> Total claims rose from 135,554 to 166,415. "
     "Claims per provider increased from 81.6 to 103.4 (+26.7%, p&lt;0.001). "
     "Cost per claim fell from $43.75 to $15.16 (−65.3%)."),
    ("<b>Proportion Shift:</b> Opioids comprised 63.9% of all pain management claims in 2014 "
     "but only 38.0% by 2023. Non-opioid modalities (gabapentinoids, muscle relaxants, NSAIDs) "
     "collectively grew from 36.1% to 62.0%. Total non-opioid claims surpassed opioid claims in 2019."),
]
for f in findings:
    elements.append(Paragraph(f, styles['BulletText']))
    elements.append(Spacer(1, 4))

elements.append(PageBreak())

# ── Table 1: Total Claims (all 10 years) ──
elements.append(Paragraph("Table 1: Total Claims by Drug Category and Year", styles['SectionHead']))
table1_data = [
    ['Year', 'Opioid', 'Gabapentinoid', 'Muscle Relaxant', 'NSAID', 'Total'],
    ['2014', '707,906', '151,485', '113,116', '135,554', '1,108,061'],
    ['2015', '632,887', '162,994', '106,785', '140,799', '1,043,465'],
    ['2016', '620,368', '179,237', '104,936', '145,562', '1,050,103'],
    ['2017', '572,680', '188,845', '126,679', '146,272', '1,034,476'],
    ['2018', '511,154', '192,547', '127,850', '145,705', '977,256'],
    ['2019', '449,991', '187,295', '137,559', '150,059', '924,904'],
    ['2020', '396,114', '190,944', '135,308', '136,056', '858,422'],
    ['2021', '374,916', '207,413', '154,581', '146,589', '883,499'],
    ['2022', '360,937', '213,107', '165,541', '157,433', '897,018'],
    ['2023', '341,801', '211,067', '180,212', '166,415', '899,495'],
]
t1 = Table(table1_data, colWidths=[45, 80, 90, 90, 80, 80])
t1.setStyle(TABLE_STYLE)
elements.append(t1)
elements.append(Spacer(1, 16))

# ── Table 2: Claims Per Provider ──
elements.append(Paragraph("Table 2: Mean Claims Per Provider by Drug Category and Year", styles['SectionHead']))
table2_data = [
    ['Year', 'Opioid', 'Gabapentinoid', 'Muscle Relaxant', 'NSAID'],
    ['2014', '190.3', '59.7', '58.2', '81.6'],
    ['2015', '174.1', '63.4', '55.4', '82.3'],
    ['2016', '170.4', '67.7', '57.2', '82.4'],
    ['2017', '163.4', '69.4', '58.0', '83.1'],
    ['2018', '150.9', '71.8', '60.8', '86.1'],
    ['2019', '139.4', '71.0', '65.0', '88.1'],
    ['2020', '139.1', '76.5', '67.2', '87.6'],
    ['2021', '134.9', '83.0', '72.7', '92.3'],
    ['2022', '135.3', '85.4', '76.4', '98.8'],
    ['2023', '135.6', '86.4', '81.6', '103.4'],
]
t2 = Table(table2_data, colWidths=[45, 90, 95, 95, 90])
t2.setStyle(TABLE_STYLE)
elements.append(t2)
elements.append(Spacer(1, 16))

# ── Table 3: Days Supply ──
elements.append(Paragraph("Table 3: Average Days Supply Per Claim", styles['SectionHead']))
table3_data = [
    ['Year', 'Opioid', 'Gabapentinoid', 'Muscle Relaxant', 'NSAID'],
    ['2014', '15.4', '33.7', '23.4', '32.9'],
    ['2015', '16.5', '34.0', '24.1', '33.5'],
    ['2016', '16.6', '34.3', '24.6', '33.9'],
    ['2017', '16.4', '34.6', '24.5', '34.5'],
    ['2018', '15.0', '35.0', '24.3', '36.0'],
    ['2019', '12.8', '35.6', '23.6', '36.3'],
    ['2020', '12.4', '34.8', '23.2', '35.9'],
    ['2021', '11.7', '34.4', '22.6', '35.3'],
    ['2022', '11.4', '34.1', '22.4', '35.2'],
    ['2023', '11.1', '34.2', '22.3', '35.2'],
]
t3 = Table(table3_data, colWidths=[45, 90, 95, 95, 90])
t3.setStyle(TABLE_STYLE)
elements.append(t3)

elements.append(PageBreak())

# ── COST ANALYSIS ──
elements.append(Paragraph("Cost Analysis", styles['SectionHead']))

elements.append(Paragraph("Table 4: Total Drug Cost by Category and Year ($ Millions)", styles['SubSectionHead']))
table4_data = [
    ['Year', 'Opioid', 'Gabapentinoid', 'Muscle Relax.', 'NSAID', 'Total'],
    ['2014', '$18.8M', '$6.1M', '$2.3M', '$5.9M', '$33.2M'],
    ['2015', '$18.2M', '$6.5M', '$2.1M', '$4.3M', '$31.0M'],
    ['2016', '$17.1M', '$6.7M', '$1.5M', '$4.2M', '$29.5M'],
    ['2017', '$12.5M', '$7.1M', '$1.8M', '$3.9M', '$25.3M'],
    ['2018', '$11.0M', '$8.3M', '$1.7M', '$3.2M', '$24.2M'],
    ['2019', '$7.6M', '$5.6M', '$1.8M', '$2.7M', '$17.7M'],
    ['2020', '$6.0M', '$3.0M', '$1.8M', '$2.5M', '$13.3M'],
    ['2021', '$5.3M', '$3.2M', '$1.9M', '$2.4M', '$12.9M'],
    ['2022', '$4.9M', '$3.3M', '$2.0M', '$2.5M', '$12.7M'],
    ['2023', '$4.4M', '$3.2M', '$1.9M', '$2.5M', '$12.0M'],
]
t4 = Table(table4_data, colWidths=[45, 80, 85, 80, 70, 70])
t4.setStyle(TABLE_STYLE)
elements.append(t4)
elements.append(Spacer(1, 12))

elements.append(Paragraph("Table 5: Cost Per Claim by Drug Category and Year", styles['SubSectionHead']))
table5_data = [
    ['Year', 'Opioid', 'Gabapentinoid', 'Muscle Relax.', 'NSAID'],
    ['2014', '$26.52', '$40.58', '$20.67', '$43.75'],
    ['2015', '$28.75', '$39.59', '$19.32', '$30.56'],
    ['2016', '$27.61', '$37.39', '$14.14', '$28.99'],
    ['2017', '$21.84', '$37.61', '$13.90', '$26.86'],
    ['2018', '$21.46', '$43.21', '$13.57', '$21.90'],
    ['2019', '$16.86', '$29.97', '$12.89', '$17.90'],
    ['2020', '$15.25', '$15.91', '$13.03', '$18.38'],
    ['2021', '$14.26', '$15.55', '$12.45', '$16.56'],
    ['2022', '$13.50', '$15.68', '$12.12', '$15.71'],
    ['2023', '$12.73', '$15.10', '$10.47', '$15.16'],
]
t5 = Table(table5_data, colWidths=[45, 90, 95, 90, 90])
t5.setStyle(TABLE_STYLE)
elements.append(t5)
elements.append(Spacer(1, 8))

elements.append(Paragraph(
    "<b>Cost Highlights:</b> Total pain management drug spending by spine surgeons fell "
    "from $33.2M (2014) to $12.0M (2023), a 63.9% decline. Opioid spending drove most of "
    "this reduction: opioid costs fell 76.8% ($18.8M → $4.4M). Opioid's share of total "
    "drug spending fell from 56.6% to 36.4%. Gabapentinoid cost per claim dropped 62.8% "
    "($40.58 → $15.10), reflecting generic gabapentin/pregabalin availability. NSAID cost "
    "per claim fell 65.3% ($43.75 → $15.16). Despite rising claim volumes for all non-opioid "
    "categories, total spending still decreased due to dramatic per-unit cost reductions.",
    styles['BodyText2']
))

elements.append(PageBreak())

# ── SPECIALTY BREAKDOWN ──
elements.append(Paragraph("Specialty Analysis: Neurosurgery vs. Orthopedic Surgery", styles['SectionHead']))

elements.append(Paragraph(
    "Orthopedic spine surgeons consistently prescribed at higher volumes per provider than "
    "neurosurgeons across all drug categories. Both specialties showed similar opioid reduction "
    "rates, but orthopedic surgeons adopted non-opioid alternatives at higher absolute rates.",
    styles['BodyText2']
))
elements.append(Spacer(1, 8))

elements.append(Paragraph("Table 6: Opioid Claims Per Provider by Specialty", styles['SubSectionHead']))
table6_data = [
    ['Year', 'Neurosurgery', 'Orthopedic Surg.', 'Neuro N', 'Ortho N'],
    ['2014', '146.5', '241.3', '2,002', '1,718'],
    ['2015', '132.2', '221.1', '1,921', '1,714'],
    ['2016', '129.5', '215.6', '1,911', '1,730'],
    ['2017', '120.4', '209.0', '1,812', '1,696'],
    ['2018', '117.0', '185.9', '1,721', '1,666'],
    ['2019', '110.1', '168.2', '1,596', '1,631'],
    ['2020', '107.6', '168.8', '1,375', '1,470'],
    ['2021', '106.4', '160.9', '1,326', '1,453'],
    ['2022', '103.9', '162.5', '1,235', '1,432'],
    ['2023', '106.6', '161.1', '1,176', '1,344'],
]
t6 = Table(table6_data, colWidths=[45, 90, 95, 70, 70])
t6.setStyle(TABLE_STYLE)
elements.append(t6)
elements.append(Spacer(1, 12))

elements.append(Paragraph("Table 7: Gabapentinoid Claims Per Provider by Specialty", styles['SubSectionHead']))
table7_data = [
    ['Year', 'Neurosurgery', 'Orthopedic Surg.', 'Neuro N', 'Ortho N'],
    ['2014', '48.8', '71.2', '1,302', '1,235'],
    ['2015', '49.9', '78.0', '1,327', '1,242'],
    ['2016', '53.7', '81.5', '1,318', '1,331'],
    ['2017', '53.3', '87.3', '1,322', '1,356'],
    ['2018', '53.6', '89.2', '1,307', '1,374'],
    ['2019', '52.4', '87.6', '1,245', '1,393'],
    ['2020', '55.5', '94.8', '1,147', '1,342'],
    ['2021', '60.5', '100.9', '1,157', '1,361'],
    ['2022', '59.4', '106.6', '1,121', '1,374'],
    ['2023', '59.7', '108.1', '1,097', '1,346'],
]
t7 = Table(table7_data, colWidths=[45, 90, 95, 70, 70])
t7.setStyle(TABLE_STYLE)
elements.append(t7)
elements.append(Spacer(1, 8))

elements.append(Paragraph(
    "<b>Specialty Highlights:</b> Neurosurgeons reduced opioid claims/provider from 146.5 to "
    "106.6 (−27.2%), while orthopedic surgeons reduced from 241.3 to 161.1 (−33.2%). "
    "Orthopedic surgeons showed greater absolute adoption of gabapentinoids (+51.8%, from "
    "71.2 to 108.1 claims/provider) compared to neurosurgeons (+22.3%, 48.8 to 59.7). "
    "The number of neurosurgery opioid prescribers fell 41.3% (2,002 → 1,176), while "
    "orthopedic opioid prescribers fell 21.8% (1,718 → 1,344).",
    styles['BodyText2']
))

elements.append(PageBreak())

# ── Figures ──
fig_files = [
    ("fig1_total_claims.png", "Figure 1: Total Pain Management Claims by Drug Category"),
    ("fig2_claims_per_provider.png", "Figure 2: Mean Claims Per Spine Surgeon Prescriber"),
    ("fig3_prescriber_counts.png", "Figure 3: Number of Spine Surgeon Prescribers by Category"),
    ("fig4_days_supply.png", "Figure 4: Average Prescription Duration (Days Supply Per Claim)"),
    ("fig5_normalized_trends.png", "Figure 5: Normalized Prescribing Trends (2014 = 100)"),
    ("fig6_drug_cost.png", "Figure 6: Total Drug Cost by Category"),
    ("fig7_proportions.png", "Figure 7: Distribution of Pain Management Claims by Category"),
    ("fig8_pct_change.png", "Figure 8: Percent Change in Prescribing Metrics, 2014–2023"),
]

for i, (fname, caption) in enumerate(fig_files):
    fpath = os.path.join(BASE, "figures", fname)
    if os.path.exists(fpath):
        elements.append(Paragraph(caption, styles['SectionHead']))
        if "fig5" in fname:
            img = Image(fpath, width=6.5*inch, height=4.5*inch)
        else:
            img = Image(fpath, width=6*inch, height=3.75*inch)
        elements.append(img)
        elements.append(Spacer(1, 12))
        if (i + 1) % 2 == 0 and i < len(fig_files) - 1:
            elements.append(PageBreak())

elements.append(PageBreak())

# ── Regression Results ──
elements.append(Paragraph("Table 8: Linear Regression Results (All 10 Years)", styles['SectionHead']))

reg_data = [
    ['Metric', 'Slope/yr', 'R²', 'P-value', '% Change'],
    ['Total Claims - Opioid', '-42,526', '0.969', '<0.001***', '-51.7%'],
    ['Total Claims - Gabapentinoid', '+6,236', '0.891', '<0.001***', '+39.3%'],
    ['Total Claims - Muscle Relaxant', '+7,873', '0.903', '<0.001***', '+59.3%'],
    ['Total Claims - NSAID', '+2,261', '0.535', '0.016*', '+22.8%'],
    ['Claims/Provider - Opioid', '-6.21', '0.893', '<0.001***', '-28.7%'],
    ['Claims/Provider - Gabapentinoid', '+2.94', '0.964', '<0.001***', '+44.7%'],
    ['Claims/Provider - Muscle Relaxant', '+2.77', '0.909', '<0.001***', '+40.3%'],
    ['Claims/Provider - NSAID', '+2.24', '0.850', '<0.001***', '+26.7%'],
    ['Prescriber Count - Opioid', '-146', '0.955', '<0.001***', '-32.3%'],
    ['Avg Days Supply - Opioid', '-0.70', '0.838', '<0.001***', '-28.3%'],
    ['Total Drug Cost - Opioid', '-$1.85M', '0.937', '<0.001***', '-76.8%'],
    ['Cost Per Claim - Opioid', '-$1.95', '0.916', '<0.001***', '-52.0%'],
    ['Cost Per Claim - Gabapentinoid', '-$3.54', '0.786', '<0.001***', '-62.8%'],
    ['Cost Per Claim - NSAID', '-$2.74', '0.840', '<0.001***', '-65.3%'],
    ['Spine Surgeon Count', '-44', '0.554', '0.014*', '-6.5%'],
    ['Pain Rx Prescriber Count', '-91', '0.894', '<0.001***', '-18.7%'],
]
t8 = Table(reg_data, colWidths=[170, 70, 50, 75, 60])
t8.setStyle(TABLE_STYLE)
elements.append(t8)
elements.append(Paragraph("* p&lt;0.05, ** p&lt;0.01, *** p&lt;0.001", styles['SmallNote']))

elements.append(PageBreak())

# ── Methods ──
elements.append(Paragraph("Methods", styles['SectionHead']))
methods_text = [
    "<b>Data Source:</b> CMS Medicare Provider Utilization and Payment Data, accessed via "
    "the CMS data.cms.gov API (Socrata Open Data API). All 10 years (2014–2023) included.",

    "<b>Spine Surgeon Identification:</b> Providers were identified from Medicare Part B "
    "Physician/Supplier data as those with provider type 'Neurological Surgery' or "
    "'Orthopedic Surgery' who billed for spine-specific CPT codes (22551, 22554, 22612, "
    "22630, 22633, 22840, 22842, 63005, 63030, 63042, 63047, 63056, 63075, 63081, 22800, "
    "22802, 22804, 22808, 22810, 22812, among others). This procedure-confirmed approach "
    "ensures the cohort represents surgeons actively performing spine procedures.",

    "<b>Drug Categories:</b> Four categories of pain management medications were analyzed: "
    "(1) <b>Opioids</b> — hydrocodone, oxycodone, tramadol, morphine, fentanyl, codeine, "
    "hydromorphone, methadone, oxymorphone, tapentadol, buprenorphine, meperidine; "
    "(2) <b>Gabapentinoids</b> — gabapentin, pregabalin; "
    "(3) <b>Muscle Relaxants</b> — cyclobenzaprine, methocarbamol, tizanidine, baclofen, "
    "metaxalone, carisoprodol, orphenadrine, dantrolene, chlorzoxazone; "
    "(4) <b>NSAIDs</b> — meloxicam, diclofenac, naproxen, celecoxib, ibuprofen, "
    "indomethacin, ketorolac, piroxicam, sulindac, etodolac, nabumetone, ketoprofen, "
    "oxaprozin, fenoprofen, flurbiprofen, mefenamic acid, tolmetin.",

    "<b>Prescribing Metrics:</b> Total Medicare Part D claims, number of unique prescribers, "
    "mean claims per provider, average days supply per claim, total drug cost, cost per claim, "
    "cost per beneficiary, and total 30-day fill equivalents were calculated for each drug "
    "category per year. Specialty-level analysis stratified results by neurosurgery vs. "
    "orthopedic surgery.",

    "<b>Statistical Analysis:</b> Linear regression was used to estimate temporal trends "
    "(slope per year) for each metric across all 10 years. Percent change was calculated "
    "from 2014 baseline to 2023.",

    "<b>Limitations:</b> The analysis is limited to Medicare Part D claims and does not "
    "capture prescriptions filled through other payers (commercial insurance, Medicaid, "
    "cash pay, or hospital/facility dispensing). Spine surgeon identification is based on "
    "Medicare billing and may not capture all spine surgeons, particularly those who do not "
    "participate in Medicare. CMS suppresses data for providers with fewer than 11 claims "
    "for a given drug, which may undercount low-volume prescribers."
]
for t in methods_text:
    elements.append(Paragraph(t, styles['BodyText2']))
    elements.append(Spacer(1, 6))

doc.build(elements)
print(f"PDF report saved to: {OUTPUT}")
