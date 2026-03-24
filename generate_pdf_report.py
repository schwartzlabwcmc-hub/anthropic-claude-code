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

elements = []

# Title page
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
    "Medicare Provider Utilization and Payment Data",
    styles['Subtitle']
))
elements.append(PageBreak())

# Key Findings
elements.append(Paragraph("Key Findings", styles['SectionHead']))
elements.append(Paragraph(
    "<b>Study Population:</b> 6,678 unique procedure-confirmed spine surgeons identified "
    "across 2014–2023 (neurosurgery + orthopedic surgery performing spine CPT codes). "
    "~4,200 spine surgeons per year in 2014 declining to ~3,925 in 2023.",
    styles['BodyText2']
))
elements.append(Spacer(1, 6))

findings = [
    ("<b>Opioid Prescribing (↓51.7%):</b> Total opioid claims fell from 707,906 (2014) to "
     "341,801 (2023). Claims per provider declined from 190.3 to 135.6 (−28.7%). "
     "Average days supply per opioid claim decreased from 15.4 to 11.1 days (−28.3%). "
     "Total opioid drug cost dropped from $18.8M to $4.4M (−76.8%)."),
    ("<b>Gabapentinoid Prescribing (↑39.3%):</b> Total claims rose from 151,485 to 211,067. "
     "Claims per provider increased from 59.7 to 86.4 (+44.7%)."),
    ("<b>Muscle Relaxant Prescribing (↑59.3%):</b> Total claims rose from 113,116 to 180,212. "
     "Claims per provider increased from 58.2 to 81.6 (+40.3%)."),
    ("<b>NSAID Prescribing (↑22.8%):</b> Total claims rose from 135,554 to 166,415. "
     "Claims per provider increased from 81.6 to 103.4 (+26.7%)."),
    ("<b>Proportion Shift:</b> Opioids comprised 63.9% of all pain management claims in 2014 "
     "but only 38.0% by 2023. Non-opioid modalities (gabapentinoids, muscle relaxants, NSAIDs) "
     "collectively grew from 36.1% to 62.0%."),
]
for f in findings:
    elements.append(Paragraph(f, styles['BulletText']))
    elements.append(Spacer(1, 4))

elements.append(PageBreak())

# Tables
elements.append(Paragraph("Table 1: Total Claims by Drug Category and Year", styles['SectionHead']))

table1_data = [
    ['Year', 'Opioid', 'Gabapentinoid', 'Muscle Relaxant', 'NSAID'],
    ['2014', '707,906', '151,485', '113,116', '135,554'],
    ['2015', '632,887', '162,994', '106,785', '140,799'],
    ['2016', '620,368', '179,237', '104,936', '145,562'],
    ['2018', '511,154', '192,547', '127,850', '145,705'],
    ['2019', '449,991', '187,295', '137,559', '150,059'],
    ['2022', '360,937', '213,107', '165,541', '157,433'],
    ['2023', '341,801', '211,067', '180,212', '166,415'],
]
t1 = Table(table1_data, colWidths=[60, 100, 100, 100, 100])
t1.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), HexColor('#16213e')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
    ('ALIGN', (0, 0), (0, -1), 'CENTER'),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#f0f0f0')]),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
]))
elements.append(t1)
elements.append(Paragraph("Note: 2017, 2020, and 2021 data unavailable due to CMS API/format changes.", styles['SmallNote']))
elements.append(Spacer(1, 16))

elements.append(Paragraph("Table 2: Mean Claims Per Provider by Drug Category and Year", styles['SectionHead']))
table2_data = [
    ['Year', 'Opioid', 'Gabapentinoid', 'Muscle Relaxant', 'NSAID'],
    ['2014', '190.3', '59.7', '58.2', '81.6'],
    ['2015', '174.1', '63.4', '55.4', '82.3'],
    ['2016', '170.4', '67.7', '57.2', '82.4'],
    ['2018', '150.9', '71.8', '60.8', '86.1'],
    ['2019', '139.4', '71.0', '65.0', '88.1'],
    ['2022', '135.3', '85.4', '76.4', '98.8'],
    ['2023', '135.6', '86.4', '81.6', '103.4'],
]
t2 = Table(table2_data, colWidths=[60, 100, 100, 100, 100])
t2.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), HexColor('#16213e')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
    ('ALIGN', (0, 0), (0, -1), 'CENTER'),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#f0f0f0')]),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
]))
elements.append(t2)
elements.append(Spacer(1, 16))

elements.append(Paragraph("Table 3: Average Days Supply Per Claim", styles['SectionHead']))
table3_data = [
    ['Year', 'Opioid', 'Gabapentinoid', 'Muscle Relaxant', 'NSAID'],
    ['2014', '15.4', '33.7', '23.4', '32.9'],
    ['2015', '16.5', '34.0', '24.1', '33.5'],
    ['2016', '16.6', '34.3', '24.6', '33.9'],
    ['2018', '15.0', '35.0', '24.3', '36.0'],
    ['2019', '12.8', '35.6', '23.6', '36.3'],
    ['2022', '11.4', '34.1', '22.4', '35.2'],
    ['2023', '11.1', '34.2', '22.3', '35.2'],
]
t3 = Table(table3_data, colWidths=[60, 100, 100, 100, 100])
t3.setStyle(TableStyle([
    ('BACKGROUND', (0, 0), (-1, 0), HexColor('#16213e')),
    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
    ('FONTSIZE', (0, 0), (-1, -1), 9),
    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
    ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
    ('ALIGN', (0, 0), (0, -1), 'CENTER'),
    ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, HexColor('#f0f0f0')]),
    ('TOPPADDING', (0, 0), (-1, -1), 4),
    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
]))
elements.append(t3)

elements.append(PageBreak())

# Figures
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
        # Use wider images for the 4-panel figure
        if "fig5" in fname:
            img = Image(fpath, width=6.5*inch, height=4.5*inch)
        else:
            img = Image(fpath, width=6*inch, height=3.75*inch)
        elements.append(img)
        elements.append(Spacer(1, 12))
        # Page break after every 2 figures
        if (i + 1) % 2 == 0 and i < len(fig_files) - 1:
            elements.append(PageBreak())

elements.append(PageBreak())

# Methods
elements.append(Paragraph("Methods", styles['SectionHead']))
methods_text = [
    "<b>Data Source:</b> CMS Medicare Provider Utilization and Payment Data, accessed via "
    "the CMS data.cms.gov API (Socrata Open Data API).",

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
    "mean claims per provider, average days supply per claim, total drug cost, and total "
    "30-day fill equivalents were calculated for each drug category per year.",

    "<b>Statistical Analysis:</b> Linear regression was used to estimate temporal trends "
    "(slope per year) for each metric. Percent change was calculated from 2014 baseline "
    "to 2023. Years with missing data (2017, 2020, 2021) were excluded from regression.",

    "<b>Limitations:</b> Data for 2017, 2020, and 2021 were unavailable due to CMS API "
    "access issues or changes in data format. The analysis is limited to Medicare Part D "
    "claims and does not capture prescriptions filled through other payers. Spine surgeon "
    "identification is based on Medicare billing and may not capture all spine surgeons."
]
for t in methods_text:
    elements.append(Paragraph(t, styles['BodyText2']))
    elements.append(Spacer(1, 6))

doc.build(elements)
print(f"PDF report saved to: {OUTPUT}")
