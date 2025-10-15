# Data Impact Analysis (pyGSI-based)


---

##  Overview

This repository contains scripts and utilities for computing **data impact diagnostics (ΔJₒ)** using **pyGSI** diagnostics output from the Rapid Refresh Forecast System (RRFS) and related DA experiments.

The analysis quantifies how observations (conventional, satellite, etc.) affect the cost function (Jo) during data assimilation cycles.  Results are saved as pickled summary files and visualization figures.

---

##  Contents

| File | Description |
|------|--------------|
| **di_driver.sh** | Main driver to control date/time loops and submit jobs via Slurm. |
| **di_submit_jobs.sh** | Slurm wrapper that loads environment modules and executes individual DI scripts. |
| **di_conv.py** | Computes Jo-diff for conventional (scalar) observation types. |
| **di_conv_uv.py** | Computes Jo-diff for conventional wind (u/v vector) observation types. |
| **di_sate.py** | Computes Jo-diff for satellite radiance observations (e.g., ABI, ATMS, CrIS, IASI). |
| **di_common.py** | Shared utilities for plotting and saving results. |
| **pyGSI/diags.py** | Local copy of pyGSI diagnostics functions for consistent results. |
| **figures/** | Directory for generated plots. |
| **pickle/** | Directory for saved pickled summary results. |
| **logs/** | Directory for Slurm output logs. |

---

##  Dependencies

These scripts require a functional python environment (e.g., `pyDAmonitor` module).  They have been tested on NOAA HPC systems Hera and Ursa, with test data staged on both HPC platforms.

##  Running the Analysis

After making sure  
1️⃣ the Python environment is correctly loaded, and  
2️⃣ the required diag files are available under the specified data path,  

one can simply run:

```bash
sh di_driver.sh
