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
````

###  Optional Detailed Channel Saving

> **Exact instruction (as requested):**  
> to disable the write of detailed satellite data information, one can change `save_channel_info` to false in the following:  
> 
> ```python
> def analyze_sate(yyyy, mm, dd, hh, data_path, save_channel_info=True):
> ```

Set it to:

```python
def analyze_sate(yyyy, mm, dd, hh, data_path, save_channel_info=False):
```


---

##  Generating Figures from Existing Pickles

If the pickle files have already been generated (from `di_conv.py`, `di_conv_uv.py`, and `di_sate.py`), you can create all **FSOI proxy** figures without re-running the full analysis by executing (see all the options in the script):

```bash
python scripts/generate_data_impact_figures.py --case sub-domain --mode both


