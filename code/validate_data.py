"""Check that the data files match the structure described in DATA_DICTIONARY.md.

Run from the repository root:  python code/validate_data.py
"""
from pathlib import Path
import sys

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

SPECIMENS_PER_LAYER_THICKNESS = {30: 40, 60: 61}
GROUPS_PER_LAYER_THICKNESS = 3   # powder heats (30 µm) or powder reuse states (60 µm)
POPULATION_SIZE = 1500
PARAMETER_SETS = {"uncalibrated", "calibrated"}

errors = []


def require_columns(df, cols, name):
    missing = [c for c in cols if c not in df.columns]
    if missing:
        errors.append(f"{name}: missing columns {missing}")
    return not missing


# Tensile data
tensile = pd.read_csv(DATA / "tensile" / "tensile_tests.csv")
if require_columns(tensile, ["specimen_id", "layer_thickness_um", "heat_id", "powder_state",
                             "yield_strength_ksi", "yield_strength_MPa_calibration",
                             "ultimate_strength_ksi", "ultimate_strength_MPa_calibration",
                             "elongation_pct"], "tensile_tests.csv"):
    if tensile.empty:
        errors.append("tensile_tests.csv: no data rows")
    if tensile["specimen_id"].duplicated().any():
        errors.append("tensile_tests.csv: duplicate specimen_id values")
    if set(tensile["layer_thickness_um"]) != set(SPECIMENS_PER_LAYER_THICKNESS):
        errors.append(f"tensile_tests.csv: layer thicknesses {sorted(set(tensile['layer_thickness_um']))} "
                      f"(expected {sorted(SPECIMENS_PER_LAYER_THICKNESS)})")
    group = tensile["heat_id"].fillna("").astype(str) + tensile["powder_state"].fillna("").astype(str)
    for lt, grp in tensile.groupby("layer_thickness_um"):
        expected = SPECIMENS_PER_LAYER_THICKNESS.get(lt)
        if len(grp) != expected:
            errors.append(f"tensile_tests.csv: {len(grp)} specimens at {lt} µm (expected {expected})")
        g = group[grp.index]
        if (g == "").any() or g.nunique() != GROUPS_PER_LAYER_THICKNESS:
            errors.append(f"tensile_tests.csv: {g.nunique()} heat/powder-state groups at {lt} µm "
                          f"(expected {GROUPS_PER_LAYER_THICKNESS}, none blank)")
    for col in ["yield_strength_ksi", "yield_strength_MPa_calibration",
                "ultimate_strength_ksi", "ultimate_strength_MPa_calibration", "elongation_pct"]:
        if (tensile[col] <= 0).any() or tensile[col].isna().any():
            errors.append(f"tensile_tests.csv: non-positive or missing values in {col}")
    for prefix in ["yield_strength", "ultimate_strength"]:
        gap = (tensile[f"{prefix}_MPa_calibration"] - tensile[f"{prefix}_ksi"] * 6.894757293168).abs()
        if (gap > 0.35).any():
            errors.append(f"tensile_tests.csv: {prefix}_MPa_calibration differs from the "
                          "as-reported ksi value by more than rounding allows")

# Weibull parameters and minimum strengths
DATASETS = {"uncalibrated_population", "experimental", "calibrated_population", "calibrated_bayesian_update"}
PARAMETERS = {"gamma", "alpha", "beta", "p01", "p10", "p90", "p99"}
weib = pd.read_csv(DATA / "weibull" / "weibull_parameters.csv")
if require_columns(weib, ["layer_thickness_um", "dataset", "method", "parameter", "estimate"],
                   "weibull_parameters.csv"):
    for lt in SPECIMENS_PER_LAYER_THICKNESS:
        post = weib[(weib["layer_thickness_um"] == lt) & (weib["method"] == "pymc_posterior")]
        have = set(zip(post["dataset"], post["parameter"]))
        missing = {(d, p) for d in DATASETS for p in PARAMETERS} - have
        if missing:
            errors.append(f"weibull_parameters.csv: {lt} µm missing {len(missing)} posterior rows")
        if (post["r_hat"] > 1.01).any():
            errors.append(f"weibull_parameters.csv: r_hat > 1.01 at {lt} µm")
    if (weib.loc[weib["parameter"].isin(["alpha", "beta"]), "estimate"] <= 0).any():
        errors.append("weibull_parameters.csv: alpha and beta must be positive")

minimum = pd.read_csv(DATA / "weibull" / "minimum_strength.csv")
for lt in SPECIMENS_PER_LAYER_THICKNESS:
    if set(minimum.loc[minimum["layer_thickness_um"] == lt, "percentile"]) != {0.01, 0.10}:
        errors.append(f"minimum_strength.csv: {lt} µm needs rows for percentiles 0.01 and 0.10")

# Simulated populations
sim = pd.read_csv(DATA / "simulated" / "simulated_populations.csv")
if require_columns(sim, ["layer_thickness_um", "property", "sample_id", "median_rank_probability",
                         "value_original_MPa", "value_calibrated_MPa"], "simulated_populations.csv"):
    expected_groups = {(lt, p) for lt in SPECIMENS_PER_LAYER_THICKNESS
                       for p in ("yield_strength", "ultimate_tensile_strength")}
    if set(map(tuple, sim[["layer_thickness_um", "property"]].drop_duplicates().values)) != expected_groups:
        errors.append("simulated_populations.csv: expected one population per layer thickness and property")
    for (lt, prop), grp in sim.groupby(["layer_thickness_um", "property"]):
        if sorted(grp["sample_id"]) != list(range(1, POPULATION_SIZE + 1)):
            errors.append(f"simulated_populations.csv: {lt} µm {prop} sample_id is not 1..{POPULATION_SIZE}")
        rank = grp["value_original_MPa"].rank(method="first")
        if (grp["median_rank_probability"] - (rank - 0.3) / (len(grp) + 0.4)).abs().max() > 1e-5:
            errors.append(f"simulated_populations.csv: {lt} µm {prop} median ranks do not match the data")
        slope, intercept = np.polyfit(grp["value_original_MPa"], grp["value_calibrated_MPa"], 1)
        resid = (grp["value_calibrated_MPa"] - (slope * grp["value_original_MPa"] + intercept)).abs().max()
        if slope <= 0 or resid > 1e-5:
            errors.append(f"simulated_populations.csv: {lt} µm {prop} calibrated values are not a linear map of the originals")

if errors:
    print("Validation FAILED:")
    for e in errors:
        print("  -", e)
    sys.exit(1)
print("All data files passed validation.")
