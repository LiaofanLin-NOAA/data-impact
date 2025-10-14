#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================
Shared Utilities for Data Impact (DI) Scripts
Author: Liaofan Lin
Created: 2025-10-14

Description:
  Provides common functions for all DI scripts, including:
    - standardized Jo-diff histogram plotting
    - consistent pickle output in legacy format
    - safe bin size computation
==============================================================
"""

import numpy as np
import matplotlib.pyplot as plt
import pickle
import os


# ============================================================
# Utility: safe histogram bin computation
# ============================================================
def compute_bins(jo_diffs):
    """Compute robust bin edges for Jo-diff histograms."""
    if len(jo_diffs) == 0:
        return np.arange(-1, 1, 0.1)
    n = len(jo_diffs)
    std = np.std(jo_diffs)
    mx, mn = np.max(jo_diffs), np.min(jo_diffs)
    binsize = (mx - mn) / np.sqrt(n) if n > 0 else 1.0
    if binsize <= 0:
        binsize = 0.1
    return np.arange(-4 * std, 4 * std, binsize)


# ============================================================
# Utility: standardized Jo-diff histogram plot
# ============================================================
def plot_jo_histogram(sensor, yyyy, mm, dd, hh,
                      jo_diffs, inv_obs_errors,
                      count_assim, count_large, count_zero,
                      data_anl, cycle,
                      outdir="./figures"):
    """
    Create and save a standardized Jo-diff histogram plot.

    Parameters
    ----------
    sensor : str
        Observation type (e.g., conv_t, conv_uv, abi_g16)
    yyyy, mm, dd, hh : str
        Date/time components
    jo_diffs : list or array
        Jo-diff values
    inv_obs_errors : list or array
        Inverse observation errors
    count_assim : int
        Number of assimilated observations
    count_large : int
        Number of |Jo-diff| > 25
    count_zero : int
        Number of Jo-diff == 0
    data_anl : DataFrame
        Full diagnostic analysis data
    cycle : str
        Cycle timestamp (YYYYMMDDHH)
    outdir : str
        Output directory for figures
    """

    os.makedirs(outdir, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    bins = compute_bins(jo_diffs)
    ax.hist(jo_diffs, bins=bins, edgecolor="black")
    ax.set_xlabel("Jo Diff")
    ax.set_ylabel("Count")
    ax.set_title(f"{sensor} {yyyy}.{mm}{dd} {hh}UTC", fontsize=14)
    ax.grid(True)

    # --- Text annotations (standardized across all scripts) ---
    plt.text(0.66, 0.82, f"Total Obs Size = {len(data_anl)}", fontsize=12,
             transform=plt.gcf().transFigure)
    plt.text(0.66, 0.78, f"Total Assim Obs Size = {count_assim}", fontsize=12,
             transform=plt.gcf().transFigure)
    plt.text(0.66, 0.74, f"Mean Jo-diff = {np.mean(jo_diffs):.4f}", fontsize=12,
             transform=plt.gcf().transFigure)
    plt.text(0.66, 0.70, f"Sum Jo-diff = {np.sum(jo_diffs):.4f}", fontsize=12,
             transform=plt.gcf().transFigure)
    plt.text(0.66, 0.66, f"Max Abs Jo-diff = {np.max(np.abs(jo_diffs)):.4f}", fontsize=12,
             transform=plt.gcf().transFigure)
    plt.text(0.66, 0.62, f"Total Size, Jo-diff > 25 = {count_large}", fontsize=12,
             transform=plt.gcf().transFigure)
    plt.text(0.66, 0.58, f"Total Size, Jo-diff is Zero = {count_zero}", fontsize=12,
             transform=plt.gcf().transFigure)
    plt.text(0.66, 0.54, f"AVG Inv Obs Error = {np.mean(inv_obs_errors):.4f}", fontsize=12,
             transform=plt.gcf().transFigure)
    plt.text(0.66, 0.50, f"STD Inv Obs Error = {np.std(inv_obs_errors):.4f}", fontsize=12,
             transform=plt.gcf().transFigure)

    outfile = os.path.join(outdir, f"{sensor}-{cycle}.png")
    plt.savefig(outfile, dpi=300, bbox_inches="tight")
    plt.close(fig)
    print(f"[FIG] Saved figure: {outfile}")


# ============================================================
# Utility: standardized legacy pickle saving
# ============================================================
def save_legacy_pickle(sensor_types,
                       total_size, assim_size,
                       mean_jo, sum_jo, max_abs_jo,
                       cycle, label="conv", outdir="./pickle"):
    """
    Save results in the legacy 6-element pickle format.

    Format:
      [sensor_types, total_size, assim_size,
       mean_jo, sum_jo, max_abs_jo]
    """
    os.makedirs(outdir, exist_ok=True)
    legacy_pickle = [
        sensor_types,
        np.array(total_size),
        np.array(assim_size),
        np.array(mean_jo),
        np.array(sum_jo),
        np.array(max_abs_jo),
    ]
    outfile = os.path.join(outdir, f"{cycle}_{label}.pkl")
    with open(outfile, "wb") as f:
        pickle.dump(legacy_pickle, f)
    print(f"[DONE] Saved results to {outfile}")
