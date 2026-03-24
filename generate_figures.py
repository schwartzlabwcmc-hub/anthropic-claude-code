#!/usr/bin/env python3
"""Generate publication-quality figures for the spine surgery prescribing analysis."""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
from scipy import stats
import os

DATA_DIR = "/home/user/anthropic-claude-code/data"
FIG_DIR = "/home/user/anthropic-claude-code/figures"
os.makedirs(FIG_DIR, exist_ok=True)

summary = pd.read_csv(os.path.join(DATA_DIR, "summary_table.csv"))
reg = pd.read_csv(os.path.join(DATA_DIR, "regression_results.csv"))

YEARS = list(range(2014, 2024))
categories = ["Opioid", "Gabapentinoid", "Muscle Relaxant", "NSAID"]
colors = {"Opioid": "#E74C3C", "Gabapentinoid": "#3498DB", "Muscle Relaxant": "#2ECC71", "NSAID": "#F39C12"}

plt.rcParams.update({
    'font.size': 11,
    'axes.titlesize': 13,
    'axes.labelsize': 12,
    'figure.dpi': 150,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
})

# ── Figure 1: Total Claims Trends ──
fig, ax = plt.subplots(figsize=(10, 6))
for cat in categories:
    cat_data = summary[summary["Drug_Category"] == cat].sort_values("Year")
    ax.plot(cat_data["Year"], cat_data["total_claims"], '-o', color=colors[cat],
            label=cat, linewidth=2, markersize=6)
ax.set_xlabel("Year")
ax.set_ylabel("Total Medicare Part D Claims")
ax.set_title("Total Pain Management Claims by Spine Surgeons, 2014-2023")
ax.legend(frameon=True, loc='center right')
ax.set_xticks(YEARS)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
ax.grid(True, alpha=0.3)
fig.savefig(os.path.join(FIG_DIR, "fig1_total_claims.png"))
plt.close()
print("Saved Figure 1: Total Claims")

# ── Figure 2: Claims Per Provider Trends ──
fig, ax = plt.subplots(figsize=(10, 6))
for cat in categories:
    cat_data = summary[summary["Drug_Category"] == cat].sort_values("Year")
    ax.plot(cat_data["Year"], cat_data["claims_per_provider"], '-o', color=colors[cat],
            label=cat, linewidth=2, markersize=6)
ax.set_xlabel("Year")
ax.set_ylabel("Mean Claims Per Provider")
ax.set_title("Mean Pain Management Claims Per Spine Surgeon Prescriber, 2014-2023")
ax.legend(frameon=True)
ax.set_xticks(YEARS)
ax.grid(True, alpha=0.3)
fig.savefig(os.path.join(FIG_DIR, "fig2_claims_per_provider.png"))
plt.close()
print("Saved Figure 2: Claims Per Provider")

# ── Figure 3: Prescriber Counts ──
fig, ax = plt.subplots(figsize=(10, 6))
for cat in categories:
    cat_data = summary[summary["Drug_Category"] == cat].sort_values("Year")
    ax.plot(cat_data["Year"], cat_data["n_prescribers"], '-o', color=colors[cat],
            label=cat, linewidth=2, markersize=6)
ax.set_xlabel("Year")
ax.set_ylabel("Number of Prescribers")
ax.set_title("Number of Spine Surgeon Prescribers by Drug Category, 2014-2023")
ax.legend(frameon=True)
ax.set_xticks(YEARS)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:,.0f}'))
ax.grid(True, alpha=0.3)
fig.savefig(os.path.join(FIG_DIR, "fig3_prescriber_counts.png"))
plt.close()
print("Saved Figure 3: Prescriber Counts")

# ── Figure 4: Average Days Supply Per Claim ──
fig, ax = plt.subplots(figsize=(10, 6))
for cat in categories:
    cat_data = summary[summary["Drug_Category"] == cat].sort_values("Year")
    ax.plot(cat_data["Year"], cat_data["avg_days_per_claim"], '-o', color=colors[cat],
            label=cat, linewidth=2, markersize=6)
ax.set_xlabel("Year")
ax.set_ylabel("Average Days Supply Per Claim")
ax.set_title("Average Prescription Duration by Drug Category, 2014-2023")
ax.legend(frameon=True)
ax.set_xticks(YEARS)
ax.grid(True, alpha=0.3)
fig.savefig(os.path.join(FIG_DIR, "fig4_days_supply.png"))
plt.close()
print("Saved Figure 4: Days Supply")

# ── Figure 5: Normalized Trends (2014=100) ──
fig, axes = plt.subplots(2, 2, figsize=(14, 10))
metrics = [
    ("total_claims", "Total Claims"),
    ("claims_per_provider", "Claims Per Provider"),
    ("n_prescribers", "Number of Prescribers"),
    ("avg_days_per_claim", "Avg Days Supply/Claim"),
]
for idx, (metric, title) in enumerate(metrics):
    ax = axes[idx // 2][idx % 2]
    for cat in categories:
        cat_data = summary[summary["Drug_Category"] == cat].sort_values("Year")
        vals = cat_data[metric].values
        baseline = vals[0]
        normalized = (vals / baseline) * 100 if baseline != 0 else vals
        ax.plot(cat_data["Year"], normalized, '-o', color=colors[cat],
                label=cat, linewidth=2, markersize=5)
    ax.axhline(y=100, color='gray', linestyle='--', alpha=0.5)
    ax.set_title(title)
    ax.set_xlabel("Year")
    ax.set_ylabel("Index (2014 = 100)")
    ax.set_xticks(YEARS)
    ax.tick_params(axis='x', rotation=45)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=9)

fig.suptitle("Normalized Prescribing Trends Among Spine Surgeons (2014 = 100)", fontsize=14, y=1.02)
fig.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "fig5_normalized_trends.png"))
plt.close()
print("Saved Figure 5: Normalized Trends")

# ── Figure 6: Total Drug Cost Trends ──
fig, ax = plt.subplots(figsize=(10, 6))
for cat in categories:
    cat_data = summary[summary["Drug_Category"] == cat].sort_values("Year")
    ax.plot(cat_data["Year"], cat_data["total_cost"] / 1e6, '-o', color=colors[cat],
            label=cat, linewidth=2, markersize=6)
ax.set_xlabel("Year")
ax.set_ylabel("Total Drug Cost ($ Millions)")
ax.set_title("Total Drug Cost by Category Among Spine Surgeons, 2014-2023")
ax.legend(frameon=True)
ax.set_xticks(YEARS)
ax.grid(True, alpha=0.3)
fig.savefig(os.path.join(FIG_DIR, "fig6_drug_cost.png"))
plt.close()
print("Saved Figure 6: Drug Cost")

# ── Figure 7: Stacked bar - proportion of claims by category ──
fig, ax = plt.subplots(figsize=(10, 6))
bottoms = np.zeros(len(YEARS))
for cat in categories:
    cat_data = summary[summary["Drug_Category"] == cat].sort_values("Year")
    year_totals = summary.groupby("Year")["total_claims"].sum()
    proportions = cat_data["total_claims"].values / year_totals.values * 100
    ax.bar(YEARS, proportions, bottom=bottoms, color=colors[cat], label=cat, width=0.7)
    bottoms += proportions
ax.set_xlabel("Year")
ax.set_ylabel("Proportion of Total Claims (%)")
ax.set_title("Distribution of Pain Management Claims by Category, 2014-2023")
ax.legend(frameon=True, loc='center right')
ax.set_xticks(YEARS)
ax.set_ylim(0, 100)
ax.grid(True, alpha=0.3, axis='y')
fig.savefig(os.path.join(FIG_DIR, "fig7_proportions.png"))
plt.close()
print("Saved Figure 7: Proportions")

# ── Figure 8: Regression forest plot ──
# Show key regression results
key_metrics = [
    "Total Claims - Opioid",
    "Total Claims - Gabapentinoid",
    "Total Claims - Muscle Relaxant",
    "Total Claims - NSAID",
    "Claims/Provider - Opioid",
    "Claims/Provider - Gabapentinoid",
    "Claims/Provider - Muscle Relaxant",
    "Claims/Provider - NSAID",
]
fig, ax = plt.subplots(figsize=(10, 6))
key_reg = reg[reg["metric"].isin(key_metrics)].copy()
key_reg["pct_change_val"] = key_reg["pct_change"]
key_reg = key_reg.set_index("metric").loc[key_metrics].reset_index()

y_pos = range(len(key_reg))
colors_bar = []
for m in key_reg["metric"]:
    for cat, c in colors.items():
        if cat in m:
            colors_bar.append(c)
            break

bars = ax.barh(y_pos, key_reg["pct_change_val"], color=colors_bar, height=0.6)
ax.set_yticks(y_pos)
ax.set_yticklabels(key_reg["metric"], fontsize=10)
ax.set_xlabel("Percent Change (2014-2023)")
ax.set_title("Percent Change in Prescribing Metrics, 2014-2023")
ax.axvline(x=0, color='black', linewidth=0.8)
ax.grid(True, alpha=0.3, axis='x')

# Add significance markers
for i, (_, row) in enumerate(key_reg.iterrows()):
    p = row["p_value"]
    sig = "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else ""))
    pct_val = row["pct_change_val"]
    offset = 2 if pct_val >= 0 else -2
    ax.text(pct_val + offset, i, f'{pct_val:+.1f}% {sig}', va='center', fontsize=9)

fig.tight_layout()
fig.savefig(os.path.join(FIG_DIR, "fig8_pct_change.png"))
plt.close()
print("Saved Figure 8: Percent Change")

print(f"\nAll figures saved to {FIG_DIR}/")
