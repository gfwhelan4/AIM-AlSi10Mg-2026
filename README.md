[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23578702.svg)](https://doi.org/10.5281/zenodo.23578702)

# Data and code for: Accelerated Qualification of Materials for Additive Manufacturing using ICME with Uncertainty Quantification

This repository has the data and code behind the conclusions of:

> H. Sandoval, D. Metcalf, A. Saboo, O. Kontsevoi, A. Love, W. Zhong, G. Whelan, F. Medina. Accelerated Qualification of Materials for Additive Manufacturing using ICME with Uncertainty Quantification. *Integrating Materials and Manufacturing Innovation* (submitted).

Archived version (cite this): https://doi.org/10.5281/zenodo.23578702

## Overview

This repository contains the experimental tensile data, simulated strength populations and analysis code used to qualify additively manufactured AlSi10Mg at two layer thicknesses (30 µm and 60 µm) with an ICME approach and uncertainty quantification. Yield-strength and ultimate-tensile-strength populations from a precipitation-strengthening model with model-based uncertainty quantification are calibrated against the tensile data. For yield strength, a Bayesian three-parameter Weibull analysis combines the experimental data with the calibrated simulated population to estimate minimum strengths at the 1st and 10th percentiles.

## Contents

| Path | Description |
|---|---|
| `data/tensile/tensile_tests.csv` | Tensile results: 40 specimens at 30 µm layer thickness across three powder heats and 61 specimens at 60 µm across three powder reuse states |
| `data/simulated/simulated_populations.csv` | 1,500-point simulated yield-strength and ultimate-tensile-strength populations, uncalibrated and calibrated, for each layer thickness |
| `data/weibull/weibull_parameters.csv` | Three-parameter Weibull fits for yield strength (Bayesian posteriors and maximum-likelihood estimates): uncalibrated population, experimental data, calibrated population and final Bayesian update |
| `data/weibull/minimum_strength.csv` | Minimum yield strengths at the 1st and 10th percentiles |
| `data/posterior/*.nc` | PyMC posterior samples (ArviZ InferenceData, NetCDF) |
| `code/weibull_calibration.ipynb` | Calibration and Bayesian Weibull analysis for one layer thickness |
| `code/run_all.py` | Runs the notebook for both layer thicknesses |
| `code/validate_data.py` | Checks the data files against `DATA_DICTIONARY.md` |
| `results/executed_notebooks/` | Executed copies of the notebook, one per layer thickness, with all outputs |
| `figures/` | Figures written by the notebook |
| `DATA_DICTIONARY.md` | Column definitions, units and allowed values for every data file |

## Materials and testing

- **Material:** AlSi10Mg, laser powder bed fusion, layer thicknesses 30 µm and 60 µm
- **Powder:** 30 µm: three powder heats (H1–H3); 60 µm: three powder reuse states (virgin, recycle 1, recycle 2)
- **Specimens:** 30 µm: ASM-C series in X, Y and Z orientations. 60 µm: T series in X, Y and Z orientations, and L series. Z is the build direction. All specimens at each layer thickness are pooled for calibration.
- **Yield strength:** 0.2 % offset method

## Simulated populations

The 1,500-point populations come from the precipitation-strengthening model with model-based uncertainty quantification. Model inputs: grain size 13 µm, dislocation density 1 × 10¹¹ m⁻². At 30 µm all variance sources are propagated; at 60 µm all variance sources are propagated with the variance reduced by 50 %.

Each population is calibrated to the experimental data at its layer thickness by matching the mean and standard deviation (step 1 below). The exact experimental values used are in `tensile_tests.csv`; for 30 µm UTS they are not available (see `DATA_DICTIONARY.md`).

## Calibration method

For yield strength at each layer thickness, `code/weibull_calibration.ipynb`:

1. Calibrates the simulated population to the experimental data by matching the mean and standard deviation, x_cal = a·x + b with a = σ_exp/σ_model and b = μ_exp − a·μ_model (Harlow, 2007).
2. Fits a three-parameter (shifted) Weibull distribution to the experimental data in PyMC with uniform priors on location γ, shape α and scale β.
3. Converts that posterior into priors by kernel density estimation and updates them with the 1,500 calibrated values.
4. Takes the 25th percentile of the posterior samples of the 1st and 10th distribution percentiles, and subtracts ⅔ × the variance due to simulation error to give the minimum strength.

Diagnostic fits to the uncalibrated and calibrated populations alone, and maximum-likelihood fits with SciPy, are included for comparison.

Sampling: NUTS, 4 chains × (1,000 tuning + 2,000 draws), `target_accept` 0.98 (0.99 for the final update), fixed random seeds. All fits have r̂ ≤ 1.01. A small number of divergent transitions after tuning are reported in `weibull_parameters.csv`.

## Reproducing the results

```bash
conda env create -f environment.yml
conda activate immi-weibull
python code/validate_data.py      # checks the data files
python code/run_all.py            # reruns the analysis for both layer thicknesses (about 10 min each on one core)
```

`run_all.py` regenerates everything in `data/weibull/`, `data/posterior/`, `figures/` and `results/executed_notebooks/`. The calibrated populations are checked against `data/simulated/simulated_populations.csv`. With the pinned package versions and fixed seeds, the posterior samples reproduce exactly; other versions give results that agree to within Monte Carlo error.

## Licenses

- Data (`data/`): [CC BY 4.0](LICENSE-DATA)
- Code (`code/`): [MIT](LICENSE)

## Citation

Please cite both the article and this archive. See `CITATION.cff`.

## Contact

Gary Whelan, QuesTek Innovations LLC, gwhelan@questek.com

## Funding

This work was funded by Lockheed Martin.
