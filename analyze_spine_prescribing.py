#!/usr/bin/env python3
"""
Longitudinal Analysis of Multimodal Pain Management Prescribing
Among Spine Surgeons in the United States, 2014-2023.

Uses CMS data.cms.gov API to query Medicare Part B (identify spine surgeons)
and Part D (prescribing data) datasets.
"""

import pandas as pd
import numpy as np
import requests
import os
import sys
import json
import time
from scipy import stats
from concurrent.futures import ThreadPoolExecutor, as_completed
import warnings
warnings.filterwarnings('ignore')

DATA_DIR = "/home/user/anthropic-claude-code/data"
os.makedirs(DATA_DIR, exist_ok=True)

YEARS = list(range(2014, 2024))
API_BASE = "https://data.cms.gov/data-api/v1/dataset"
MAX_PAGE_SIZE = 5000
MAX_WORKERS = 8  # concurrent API requests

# ── API UUIDs by year ──
PART_B_UUIDS = {
    2014: "f63b48ae-946e-48f7-9f56-327a68da4e0b",
    2015: "f8cdb11a-d5f7-4fbe-aac4-05abc8ee2c83",
    2016: "7918e22a-fbfb-4a07-9f59-f8aab2b757d4",
    2017: "85bf3c9c-2244-490d-ad7d-c34e4c28f8ea",
    2018: "fb6d9fe8-38c1-4d24-83d4-0b7b291000b2",
    2019: "867b8ac7-ccb7-4cc9-873d-b24340d89e32",
    2020: "c957b49e-1323-49e7-8678-c09da387551d",
    2021: "31dc2c47-f297-4948-bfb4-075e1bec3a02",
    2022: "e650987d-01b7-4f09-b75e-b0b075afbf98",
    2023: "92396110-2aed-4d63-a6a2-5d6207d46a29",
}

PART_D_UUIDS = {
    2014: "0779bc8d-18dd-40b8-9d61-7addc8b0daf1",
    2015: "1d650894-8afe-4056-ba31-a85cb0e3cee6",
    2016: "25106f9d-0eb8-4ba7-b237-486ee87d910a",
    2017: "05f108dd-76c4-49f4-9fdc-788d8f4251ec",
    2018: "802fe556-311f-4962-8d75-d5f4ff405884",
    2019: "2a6705e6-7a1e-460c-ba22-35249a531918",
    2020: "7795fe20-e80e-435a-a9ed-d2d65e05feeb",
    2021: "f68114ed-f854-4ffc-9c6e-ed78b5e2f8d0",
    2022: "b101b457-ffa4-49bb-8fd9-27c1266086e2",
    2023: "9552739e-3d05-4c1b-8eff-ecabf391e2e5",
}

# ── Spine Surgery CPT Codes ──
SPINE_CPT_CODES = set()

# Decompression (laminectomy, laminotomy, foraminotomy)
for c in range(63001, 63049):
    SPINE_CPT_CODES.add(str(c))
for c in range(63055, 63067):
    SPINE_CPT_CODES.add(str(c))
for c in [63075, 63076, 63077, 63078]:
    SPINE_CPT_CODES.add(str(c))

# Posterior/posterolateral fusion
for c in range(22600, 22635):
    SPINE_CPT_CODES.add(str(c))
# Anterior/anterolateral fusion
for c in range(22548, 22586):
    SPINE_CPT_CODES.add(str(c))
# Posterior arthrodesis (lateral extracavitary)
for c in range(22800, 22813):
    SPINE_CPT_CODES.add(str(c))

# Instrumentation
for c in range(22840, 22856):
    SPINE_CPT_CODES.add(str(c))

# Discectomy
SPINE_CPT_CODES.add("62380")
for c in range(63020, 63043):
    SPINE_CPT_CODES.add(str(c))

# Vertebral augmentation (vertebroplasty/kyphoplasty)
for c in range(22510, 22516):
    SPINE_CPT_CODES.add(str(c))

# Corpectomy
for c in range(63081, 63092):
    SPINE_CPT_CODES.add(str(c))

# Artificial disc replacement
for c in range(22856, 22866):
    SPINE_CPT_CODES.add(str(c))

# Spinal cord stimulator implantation
for c in [63650, 63655, 63661, 63662, 63663, 63664, 63685, 63688]:
    SPINE_CPT_CODES.add(str(c))

SPINE_SPECIALTIES = ["Neurosurgery", "Orthopedic Surgery"]

# ── Drug Classification ──
OPIOIDS = [
    "oxycodone", "hydrocodone", "morphine", "codeine", "tramadol",
    "fentanyl", "methadone", "hydromorphone", "oxymorphone", "meperidine",
    "tapentadol", "buprenorphine", "levorphanol", "butorphanol",
    "pentazocine", "nalbuphine", "dihydrocodeine",
]

GABAPENTINOIDS = [
    "gabapentin", "pregabalin",
]

MUSCLE_RELAXANTS = [
    "cyclobenzaprine", "methocarbamol", "tizanidine", "baclofen",
    "carisoprodol", "metaxalone", "orphenadrine", "dantrolene",
    "chlorzoxazone",
]

NSAIDS = [
    "ibuprofen", "naproxen", "meloxicam", "diclofenac", "celecoxib",
    "indomethacin", "ketorolac", "piroxicam", "sulindac", "etodolac",
    "nabumetone", "oxaprozin", "ketoprofen", "flurbiprofen",
    "meclofenamate", "fenoprofen", "tolmetin",
]


def classify_drug(generic_name):
    """Classify a drug into one of the four categories."""
    if not generic_name or not isinstance(generic_name, str):
        return None
    name_lower = generic_name.lower().strip()
    for drug in OPIOIDS:
        if drug in name_lower:
            return "Opioid"
    for drug in GABAPENTINOIDS:
        if drug in name_lower:
            return "Gabapentinoid"
    for drug in MUSCLE_RELAXANTS:
        if drug in name_lower:
            return "Muscle Relaxant"
    for drug in NSAIDS:
        if drug in name_lower:
            return "NSAID"
    return None


def api_get(url, params, max_retries=4):
    """Make an API GET request with retries and exponential backoff."""
    for attempt in range(max_retries):
        try:
            resp = requests.get(url, params=params, timeout=120)
            resp.raise_for_status()
            return resp.json()
        except Exception as e:
            if attempt < max_retries - 1:
                wait = 2 ** (attempt + 1)
                time.sleep(wait)
            else:
                print(f"\n  API error after {max_retries} attempts: {e}")
                return []


def api_get_stats(uuid, filters=None):
    """Get the count of records matching filters."""
    url = f"{API_BASE}/{uuid}/data/stats"
    params = filters or {}
    data = api_get(url, params)
    if isinstance(data, dict):
        return data.get("found_rows", 0)
    return 0


def api_fetch_all(uuid, filters=None, columns=None):
    """Fetch all records matching filters using pagination."""
    url = f"{API_BASE}/{uuid}/data"
    params = dict(filters) if filters else {}
    params["size"] = MAX_PAGE_SIZE

    # First get total count
    total = api_get_stats(uuid, filters)
    if total == 0:
        return []

    all_records = []
    offsets = list(range(0, total, MAX_PAGE_SIZE))

    def fetch_page(offset):
        p = dict(params)
        p["offset"] = offset
        return api_get(url, p)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(fetch_page, off): off for off in offsets}
        for future in as_completed(futures):
            result = future.result()
            if result:
                all_records.extend(result)

    return all_records


def fetch_spine_npis_for_year(year):
    """Fetch spine surgeon NPIs for a given year using Part B API."""
    cache_file = os.path.join(DATA_DIR, f"spine_npis_{year}.json")
    if os.path.exists(cache_file):
        with open(cache_file) as f:
            data = json.load(f)
        print(f"  [{year}] Loaded {len(data)} spine surgeon NPIs from cache")
        return set(data)

    uuid = PART_B_UUIDS[year]
    spine_npis = set()

    for specialty in SPINE_SPECIALTIES:
        print(f"  [{year}] Fetching {specialty} spine procedure records...")

        # Query each spine CPT code individually (most fit in one page)
        def fetch_cpt(cpt_code):
            records = api_fetch_all(uuid, {
                "filter[Rndrng_Prvdr_Type]": specialty,
                "filter[HCPCS_Cd]": cpt_code,
            })
            return {r["Rndrng_NPI"] for r in records if "Rndrng_NPI" in r}

        # Use concurrent requests across CPT codes
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(fetch_cpt, cpt): cpt for cpt in SPINE_CPT_CODES}
            done = 0
            for future in as_completed(futures):
                npis = future.result()
                spine_npis.update(npis)
                done += 1
                sys.stdout.write(f"\r    {specialty}: {done}/{len(SPINE_CPT_CODES)} codes, {len(spine_npis)} NPIs so far")
                sys.stdout.flush()

        print()

    print(f"  [{year}] Total spine surgeon NPIs: {len(spine_npis)}")

    with open(cache_file, 'w') as f:
        json.dump(list(spine_npis), f)

    return spine_npis


def fetch_prescribing_for_year(year, spine_npis):
    """Fetch pain management prescribing data for spine surgeons from Part D API."""
    cache_file = os.path.join(DATA_DIR, f"prescribing_{year}.csv")
    if os.path.exists(cache_file):
        df = pd.read_csv(cache_file, dtype={"Prscrbr_NPI": str})
        print(f"  [{year}] Loaded {len(df)} prescribing records from cache")
        return df

    uuid = PART_D_UUIDS[year]
    all_records = []

    for specialty in SPINE_SPECIALTIES:
        print(f"  [{year}] Fetching {specialty} prescriptions...")
        records = api_fetch_all(uuid, {"filter[Prscrbr_Type]": specialty})
        print(f"    Got {len(records)} raw records")

        # Filter for spine surgeon NPIs and classify drugs
        for r in records:
            npi = r.get("Prscrbr_NPI", "")
            if npi in spine_npis:
                gnrc = r.get("Gnrc_Name", "")
                cat = classify_drug(gnrc)
                if cat:
                    all_records.append({
                        "Prscrbr_NPI": npi,
                        "Prscrbr_Type": r.get("Prscrbr_Type", ""),
                        "Gnrc_Name": gnrc,
                        "Brnd_Name": r.get("Brnd_Name", ""),
                        "Drug_Category": cat,
                        "Tot_Clms": pd.to_numeric(r.get("Tot_Clms"), errors="coerce"),
                        "Tot_30day_Fills": pd.to_numeric(r.get("Tot_30day_Fills"), errors="coerce"),
                        "Tot_Day_Suply": pd.to_numeric(r.get("Tot_Day_Suply"), errors="coerce"),
                        "Tot_Drug_Cst": pd.to_numeric(r.get("Tot_Drug_Cst"), errors="coerce"),
                        "Tot_Benes": pd.to_numeric(r.get("Tot_Benes"), errors="coerce"),
                        "Year": year,
                    })

    if all_records:
        df = pd.DataFrame(all_records)
        df.to_csv(cache_file, index=False)
        print(f"  [{year}] Saved {len(df)} pain Rx records")
        return df
    else:
        print(f"  [{year}] No matching pain Rx records")
        return pd.DataFrame()


def run_regression(years, values, label):
    """Run linear regression and return results."""
    x = np.array(years, dtype=float)
    y = np.array(values, dtype=float)
    mask = ~np.isnan(y)
    x, y = x[mask], y[mask]
    if len(x) < 3:
        return None
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    return {
        "metric": label,
        "slope_per_year": slope,
        "r_squared": r_value**2,
        "p_value": p_value,
        "intercept": intercept,
        "std_err": std_err,
        "first_value": y[0],
        "last_value": y[-1],
        "pct_change": ((y[-1] - y[0]) / y[0]) * 100 if y[0] != 0 else None,
    }


def main():
    print("=" * 70)
    print("LONGITUDINAL ANALYSIS OF MULTIMODAL PAIN MANAGEMENT PRESCRIBING")
    print("AMONG SPINE SURGEONS IN THE UNITED STATES, 2014-2023")
    print("=" * 70)
    print(f"\nUsing CMS data.cms.gov API")
    print(f"Spine CPT codes: {len(SPINE_CPT_CODES)} codes")
    print()

    # ── STEP 1: Identify spine surgeons ──
    print("STEP 1: Identifying spine surgeons from Medicare Part B claims")
    print("-" * 70)

    all_spine_npis = {}
    cumulative_npis = set()

    for year in YEARS:
        npis = fetch_spine_npis_for_year(year)
        all_spine_npis[year] = npis
        cumulative_npis.update(npis)

    print(f"\nTotal unique spine surgeon NPIs across all years: {len(cumulative_npis)}")

    # ── STEP 2: Extract prescribing data ──
    print("\n\nSTEP 2: Extracting prescribing data from Medicare Part D")
    print("-" * 70)

    all_prescribing = []
    for year in YEARS:
        npis = all_spine_npis[year]
        if not npis:
            continue
        df = fetch_prescribing_for_year(year, npis)
        if len(df) > 0:
            all_prescribing.append(df)

    if not all_prescribing:
        print("ERROR: No prescribing data collected. Exiting.")
        sys.exit(1)

    rx_data = pd.concat(all_prescribing, ignore_index=True)
    print(f"\nTotal pain management prescribing records: {len(rx_data):,}")
    rx_data.to_csv(os.path.join(DATA_DIR, "combined_prescribing.csv"), index=False)

    # ── STEP 3: Analysis ──
    print("\n\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)

    categories = ["Opioid", "Gabapentinoid", "Muscle Relaxant", "NSAID"]

    # Table 1: Spine surgeon counts
    print("\n\n── Table 1: Spine Surgeon Prescriber Counts by Year ──")
    print(f"{'Year':<8}{'Spine Surgeons':<20}{'Pain Rx Prescribers':<22}{'% Prescribing':<15}")
    print("-" * 65)

    yearly_stats = {}
    for year in YEARS:
        n_surgeons = len(all_spine_npis[year])
        year_rx = rx_data[rx_data["Year"] == year]
        n_prescribers = year_rx["Prscrbr_NPI"].nunique()
        pct = (n_prescribers / n_surgeons * 100) if n_surgeons > 0 else 0
        yearly_stats[year] = {"n_surgeons": n_surgeons, "n_prescribers": n_prescribers, "pct_prescribing": pct}
        print(f"{year:<8}{n_surgeons:<20}{n_prescribers:<22}{pct:<15.1f}")

    # Build summary data
    summary = {}
    for cat in categories:
        summary[cat] = {}
        for year in YEARS:
            cat_year = rx_data[(rx_data["Year"] == year) & (rx_data["Drug_Category"] == cat)]
            total_claims = cat_year["Tot_Clms"].sum()
            n_prescribers = cat_year["Prscrbr_NPI"].nunique()
            total_day_supply = cat_year["Tot_Day_Suply"].sum()
            total_cost = cat_year["Tot_Drug_Cst"].sum()
            total_benes = cat_year["Tot_Benes"].sum()
            total_30day = cat_year["Tot_30day_Fills"].sum()
            claims_per_prov = total_claims / n_prescribers if n_prescribers > 0 else 0
            avg_days = total_day_supply / total_claims if total_claims > 0 else 0

            summary[cat][year] = {
                "total_claims": total_claims,
                "n_prescribers": n_prescribers,
                "total_day_supply": total_day_supply,
                "total_cost": total_cost,
                "total_benes": total_benes,
                "total_30day_fills": total_30day,
                "claims_per_provider": claims_per_prov,
                "avg_days_per_claim": avg_days,
            }

    # Table 2: Total claims
    print("\n\n── Table 2: Total Claims by Drug Category and Year ──")
    header = f"{'Year':<8}" + "".join(f"{cat:>18}" for cat in categories)
    print(header)
    print("-" * 80)
    for year in YEARS:
        row = f"{year:<8}"
        for cat in categories:
            row += f"{summary[cat][year]['total_claims']:>18,.0f}"
        print(row)

    # Table 3: Claims per provider
    print("\n\n── Table 3: Mean Claims Per Provider by Drug Category and Year ──")
    print(header)
    print("-" * 80)
    for year in YEARS:
        row = f"{year:<8}"
        for cat in categories:
            row += f"{summary[cat][year]['claims_per_provider']:>18.1f}"
        print(row)

    # Table 4: Average days supply per claim
    print("\n\n── Table 4: Average Days Supply Per Claim by Drug Category and Year ──")
    print(header)
    print("-" * 80)
    for year in YEARS:
        row = f"{year:<8}"
        for cat in categories:
            row += f"{summary[cat][year]['avg_days_per_claim']:>18.1f}"
        print(row)

    # Table 5: Prescriber counts
    print("\n\n── Table 5: Number of Prescribers by Drug Category and Year ──")
    print(header)
    print("-" * 80)
    for year in YEARS:
        row = f"{year:<8}"
        for cat in categories:
            row += f"{summary[cat][year]['n_prescribers']:>18,}"
        print(row)

    # Table 6: Total drug cost
    print("\n\n── Table 6: Total Drug Cost ($) by Drug Category and Year ──")
    print(header)
    print("-" * 80)
    for year in YEARS:
        row = f"{year:<8}"
        for cat in categories:
            row += f"{summary[cat][year]['total_cost']:>18,.0f}"
        print(row)

    # ── Regression Analysis ──
    print("\n\n── Table 7: Linear Regression Results (Temporal Trends 2014-2023) ──")
    print(f"{'Metric':<55}{'Slope/yr':>12}{'R²':>10}{'P-value':>12}{'Sig':>5}{'% Change':>12}")
    print("-" * 106)

    regression_results = []

    for cat in categories:
        for metric_name, metric_key in [
            ("Total Claims", "total_claims"),
            ("Claims/Provider", "claims_per_provider"),
            ("Prescriber Count", "n_prescribers"),
            ("Avg Days Supply/Claim", "avg_days_per_claim"),
            ("Total Drug Cost", "total_cost"),
        ]:
            values = [summary[cat][y][metric_key] for y in YEARS]
            result = run_regression(YEARS, values, f"{metric_name} - {cat}")
            if result:
                regression_results.append(result)

    # Overall trends
    for label, key in [("Spine Surgeon Count", "n_surgeons"), ("Pain Rx Prescriber Count", "n_prescribers")]:
        values = [yearly_stats[y][key] for y in YEARS]
        result = run_regression(YEARS, values, label)
        if result:
            regression_results.append(result)

    for r in regression_results:
        pct = f"{r['pct_change']:.1f}%" if r['pct_change'] is not None else "N/A"
        if r['p_value'] < 0.001:
            sig = "***"
        elif r['p_value'] < 0.01:
            sig = "**"
        elif r['p_value'] < 0.05:
            sig = "*"
        else:
            sig = "ns"
        print(f"{r['metric']:<55}{r['slope_per_year']:>12.2f}{r['r_squared']:>10.4f}{r['p_value']:>12.6f}{sig:>5}{pct:>12}")

    # ── Key Findings ──
    print("\n\n" + "=" * 70)
    print("SUMMARY OF KEY FINDINGS")
    print("=" * 70)

    for cat in categories:
        tc = [summary[cat][y]["total_claims"] for y in YEARS]
        cpp = [summary[cat][y]["claims_per_provider"] for y in YEARS]
        np_ = [summary[cat][y]["n_prescribers"] for y in YEARS]
        tc_change = ((tc[-1] - tc[0]) / tc[0] * 100) if tc[0] > 0 else 0
        cpp_change = ((cpp[-1] - cpp[0]) / cpp[0] * 100) if cpp[0] > 0 else 0
        np_change = ((np_[-1] - np_[0]) / np_[0] * 100) if np_[0] > 0 else 0

        tc_reg = run_regression(YEARS, tc, "")
        cpp_reg = run_regression(YEARS, cpp, "")
        np_reg = run_regression(YEARS, np_, "")

        print(f"\n{cat.upper()}:")
        print(f"  Total claims: {tc[0]:,.0f} (2014) → {tc[-1]:,.0f} (2023), change: {tc_change:+.1f}%")
        if tc_reg:
            print(f"    Trend: slope={tc_reg['slope_per_year']:+.1f}/yr, R²={tc_reg['r_squared']:.3f}, p={tc_reg['p_value']:.4f}")
        print(f"  Claims/provider: {cpp[0]:.1f} (2014) → {cpp[-1]:.1f} (2023), change: {cpp_change:+.1f}%")
        if cpp_reg:
            print(f"    Trend: slope={cpp_reg['slope_per_year']:+.2f}/yr, R²={cpp_reg['r_squared']:.3f}, p={cpp_reg['p_value']:.4f}")
        print(f"  Prescribers: {np_[0]:,.0f} (2014) → {np_[-1]:,.0f} (2023), change: {np_change:+.1f}%")

    print(f"\n\nSTUDY POPULATION:")
    print(f"  {len(cumulative_npis):,} unique procedure-confirmed spine surgeons (2014-2023)")
    print(f"  {yearly_stats[2014]['n_surgeons']:,} (2014) → {yearly_stats[2023]['n_surgeons']:,} (2023)")

    # Save results
    reg_df = pd.DataFrame(regression_results)
    reg_df.to_csv(os.path.join(DATA_DIR, "regression_results.csv"), index=False)

    rows = []
    for year in YEARS:
        for cat in categories:
            s = summary[cat][year]
            rows.append({"Year": year, "Drug_Category": cat, **s})
    summary_df = pd.DataFrame(rows)
    summary_df.to_csv(os.path.join(DATA_DIR, "summary_table.csv"), index=False)

    print(f"\nResults saved to {DATA_DIR}/")
    print("  - summary_table.csv")
    print("  - regression_results.csv")
    print("  - combined_prescribing.csv")


if __name__ == "__main__":
    main()
