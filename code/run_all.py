"""Run the calibration notebook for every layer thickness and keep the executed copies.

Run from the repository root:  python code/run_all.py
"""
from pathlib import Path
import papermill as pm

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "executed_notebooks"
OUT.mkdir(parents=True, exist_ok=True)

for lt in (30, 60):
    pm.execute_notebook(
        ROOT / "code" / "weibull_calibration.ipynb",
        OUT / f"weibull_calibration_lt{lt}um.ipynb",
        parameters={"LAYER_THICKNESS_UM": lt},
        cwd=str(ROOT),
    )
    print(f"{lt} µm done")
