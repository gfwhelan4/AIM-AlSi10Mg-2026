# Data dictionary

All files are UTF-8 CSV with a single header row, comma-separated, `.` as decimal separator. Missing values are left empty. Units are in the column names.

## `data/tensile/tensile_tests.csv`

One row per specimen: 40 specimens at 30 µm (three powder heats, three build orientations) and 61 specimens at 60 µm (three powder reuse states; 41 T-series specimens in three build orientations and 20 L-series specimens). All specimens were used in the calibration. Columns in US customary units are the values as reported and are unmodified. The 60 µm records report fewer quantities than the 30 µm records; columns not reported are empty. SI columns are converted from them (1 ksi = 6.894757 MPa, 1 msi = 6.894757 GPa, 1 in² = 645.16 mm², 1 lbf = 4.448222 N) and rounded to a precision matching the source.

`yield_strength_MPa_calibration` and `ultimate_strength_MPa_calibration` hold the values used as the experimental input to the calibration. Use these to reproduce the calibration.

- Yield strength (30 and 60 µm) and UTS (60 µm): these values came from a higher-precision source than the as-reported ksi values, so they differ from the converted columns by up to ±0.35 MPa (half of 0.1 ksi). That source is not available.
- UTS at 30 µm: the values used in the calibration are not available, so `ultimate_strength_MPa_calibration` is the as-reported ksi value converted to MPa (`ultimate_strength_calibration_source` = `converted_from_ksi`). The deposited calibrated 30 µm UTS population was produced from the unavailable values (mean 259.57 MPa, population SD 6.09 MPa); calibrating against the converted values instead (mean 259.59 MPa, population SD 6.19 MPa) gives a population that differs slightly.

| Column | Type | Units | Description |
|---|---|---|---|
| `test_no` | integer | — | Row number within the layer thickness, in the order of the original records |
| `specimen_id` | string | — | Specimen identifier as recorded. 30 µm: `ASM-C-<heat><build>-T-<orientation>-<n>`; 60 µm: `T<orientation><n>[b|c]` or `L<n>[b|c]` |
| `layer_thickness_um` | integer | µm | Build layer thickness |
| `machine` | string | — | L-PBF machine; empty if not recorded |
| `specimen_series` | string | — | `ASM-C` (30 µm), `T` or `L` (60 µm) |
| `heat_id` | string | — | Powder heat (`H1`, `H2`, `H3`), from the first digit of the build code (30 µm only) |
| `powder_state` | string | — | Powder reuse state: `Virgin`, `Recycle 1`, `Recycle 2` (60 µm only) |
| `build_id` | string | — | Build code from the specimen ID (30 µm only) |
| `build_orientation` | string | — | `X`, `Y` or `Z`; Z is the build direction. Empty for L-series specimens |
| `cross_section_area_in2` | float | in² | Initial cross-sectional area (as reported) |
| `youngs_modulus_msi` | float | msi | Young's modulus (as reported) |
| `poissons_ratio` | float | — | Poisson's ratio (as reported) |
| `elastic_strain_rate_per_min` | float | min⁻¹ | Strain rate in the elastic region, in/in/min (as reported) |
| `yield_strength_ksi` | float | ksi | 0.2 % offset yield strength (as reported) |
| `yield_load_lbf` | integer | lbf | Load at 0.2 % offset yield (as reported) |
| `strain_at_yield` | float | — | Engineering strain at yield, in/in (as reported) |
| `ultimate_strength_ksi` | float | ksi | Ultimate tensile strength (as reported) |
| `ultimate_load_lbf` | integer | lbf | Maximum load (as reported) |
| `strain_at_ultimate` | float | — | Engineering strain at ultimate, in/in (as reported) |
| `elongation_pct` | float | % | Elongation at fracture (as reported) |
| `reduction_of_area_pct` | float | % | Reduction of area (as reported; may be empty) |
| `yield_strength_MPa_calibration` | float | MPa | Yield strength used as calibration input (see above) |
| `ultimate_strength_MPa_calibration` | float | MPa | UTS used as calibration input (see above) |
| `ultimate_strength_calibration_source` | string | — | `calibration_input` or `converted_from_ksi` (see above) |
| `cross_section_area_mm2` | float | mm² | Converted |
| `youngs_modulus_GPa` | float | GPa | Converted |
| `elastic_strain_rate_per_s` | float | s⁻¹ | Converted |
| `yield_strength_MPa` | float | MPa | Converted from `yield_strength_ksi` |
| `yield_load_N` | integer | N | Converted |
| `ultimate_strength_MPa` | float | MPa | Converted |
| `ultimate_load_N` | integer | N | Converted |
| `notes` | string | — | Data-quality notes; empty if none |

## `data/weibull/weibull_parameters.csv`

Three-parameter Weibull fits, written by `code/weibull_calibration.ipynb`. Long format: one row per layer thickness × dataset × method × parameter.

The distribution is F(x) = 1 − exp(−((x − γ)/β)^α) for x ≥ γ, with location γ (`gamma`), shape α (`alpha`) and scale β (`beta`).

| Column | Type | Units | Description |
|---|---|---|---|
| `layer_thickness_um` | integer | µm | Build layer thickness |
| `dataset` | string | — | `uncalibrated_population`: simulated population from the model-based UQ; `experimental`: tensile data; `calibrated_population`: simulated population after Harlow calibration; `calibrated_bayesian_update`: experimental posterior updated with the calibrated population (final result) |
| `method` | string | — | `pymc_posterior` (Bayesian, NUTS) or `scipy_mle` (maximum likelihood, `scipy.stats.weibull_min.fit`) |
| `parameter` | string | — | `gamma`, `alpha`, `beta`, or a distribution percentile `p01`, `p10`, `p90`, `p99` |
| `estimate` | float | MPa (dimensionless for `alpha`) | Posterior mean, or the maximum-likelihood estimate |
| `sd` | float | as `estimate` | Posterior standard deviation (posterior only) |
| `median` | float | as `estimate` | Posterior median (posterior only) |
| `q25` | float | as `estimate` | Posterior 25th percentile (posterior only) |
| `hdi_2.5`, `hdi_97.5` | float | as `estimate` | Bounds of the 95 % highest-density interval (posterior only) |
| `r_hat` | float | — | Gelman–Rubin convergence statistic (posterior only) |
| `ess_bulk` | float | — | Bulk effective sample size (posterior only) |
| `divergences` | integer | — | Divergent NUTS transitions after tuning (posterior only) |

## `data/weibull/minimum_strength.csv`

Minimum strengths from the final posterior (`calibrated_bayesian_update`). One row per layer thickness × percentile.

| Column | Type | Units | Description |
|---|---|---|---|
| `layer_thickness_um` | integer | µm | Build layer thickness |
| `percentile` | float | — | Distribution percentile: 0.01 (1st) or 0.10 (10th) |
| `posterior_q25_MPa` | float | MPa | 25th percentile of the posterior samples of that distribution percentile |
| `variance_due_to_simulation` | float | MPa² | Mean squared difference between sorted experimental values and sorted subsamples of the calibrated population (20,000 subsamples) |
| `variance_due_to_simulation_stderr` | float | MPa² | Standard error of the above |
| `guaranteed_minimum_strength_MPa` | float | MPa | `posterior_q25_MPa` − ⅔ × `variance_due_to_simulation` |

## `data/simulated/simulated_populations.csv`

Simulated yield-strength and ultimate-tensile-strength populations from the precipitation-strengthening model, before and after calibration. One row per simulated sample; 1,500 rows per layer thickness × property. Rows keep the original sampling order. `value_original_MPa` and `value_calibrated_MPa` in the same row are the same sample before and after calibration.

| Column | Type | Units | Description |
|---|---|---|---|
| `layer_thickness_um` | integer | µm | Build layer thickness |
| `property` | string | — | `yield_strength` (0.2 % offset) or `ultimate_tensile_strength` (engineering) |
| `grain_size_um` | float | µm | Grain size used in the model |
| `dislocation_density_per_m2` | float | m⁻² | Dislocation density used in the model |
| `variance_case` | string | — | Variance sources propagated: `all`, or `all_50pct_reduced` |
| `sample_id` | integer | — | 1–1500, in sampling order |
| `median_rank_probability` | float | — | Bernard median rank, (i − 0.3)/(n + 0.4), of the sample within its population; identical for original and calibrated values |
| `value_original_MPa` | float | MPa | Simulated strength, uncalibrated |
| `value_calibrated_MPa` | float | MPa | Simulated strength, calibrated |

## `data/posterior/lt<layer thickness>um_<dataset>.nc`

Posterior samples for each PyMC fit (4 chains × 2,000 draws), as ArviZ `InferenceData` in NetCDF. `<dataset>` matches the `dataset` column of `weibull_parameters.csv`. Open with `arviz.from_netcdf(path)`. Contains the posterior, sample statistics and observed data groups.
