#!/usr/bin/env python3
"""
Plot spatial distribution of detailed conventional data.

Reads pickle files created by di_conv.py (option SAVE_DETAIL=true),
stored in ./pickle_detail, and generates one map per file showing
the observation locations. Figures are written to ./figures_detail.

Expected pickle content:
  - jo_diff
  - inv_obs_errors
  - latitude
  - longitude
  - pressure
  - observation_type

Usage:
  - python scripts_post/plot_conv_spatial_detail.py 2024092706 2024092706
  - python scripts_post/plot_conv_spatial_detail.py 2024092706 2024092900

"""

import os
import sys
import glob
import pickle
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

try:
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    HAS_CARTOPY = True
except ImportError:
    HAS_CARTOPY = False
    print("[WARN] cartopy not found. Using simple lat/lon plot.")


# ---------------------------------------------------------
# Utility
# ---------------------------------------------------------

def extract_cycle_from_filename(fname):
    """
    Example: "2024121306_conv_ps_detail.pkl" → 2024121306
    """
    base = os.path.basename(fname)
    cycle_str = base.split("_")[0]
    return int(cycle_str)


def cycle_range(start_cycle, end_cycle):
    """Generate all hourly cycles between start_cycle and end_cycle."""
    dt_start = datetime.strptime(str(start_cycle), "%Y%m%d%H")
    dt_end   = datetime.strptime(str(end_cycle), "%Y%m%d%H")

    cycles = set()
    dt = dt_start
    while dt <= dt_end:
        cycles.add(int(dt.strftime("%Y%m%d%H")))
        dt += timedelta(hours=1)

    return cycles


# ---------------------------------------------------------
# Plotting
# ---------------------------------------------------------

def plot_spatial_distribution(pkl_path, outdir):
    with open(pkl_path, "rb") as f:
        data = pickle.load(f)

    lat = np.asarray(data["latitude"])
    lon = np.asarray(data["longitude"]) 

    basename = os.path.basename(pkl_path)
    parts = basename.replace(".pkl", "").split("_")
    cycle  = parts[0]
    sensor = "_".join(parts[1:-1])

    # Create figure
    fig = plt.figure(figsize=(10, 5))

    if not HAS_CARTOPY:
        sys.exit("[ERROR] Cartopy is required for this script. Please install cartopy.")
    
    # Projection centered at 180° so RRFS-A domain looks correct
    proj = ccrs.PlateCarree(central_longitude=180)
    ax = plt.axes(projection=proj)
    
    # RRFS-A domain: 0–85N, 140E–10W  (stored as 140 → 350 in 0–360)
    ax.set_extent([140, 350, 0, 85], crs=ccrs.PlateCarree())
    
    # Coastlines, borders, states
    ax.add_feature(cfeature.COASTLINE, linewidth=0.7)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)
    try:
        ax.add_feature(cfeature.STATES, linewidth=0.4)
    except:
        print("[WARN] Could not load U.S. state boundaries.")
    
    # ----------------------------------------------------------
    # Gridlines every 10°, small labels
    # ----------------------------------------------------------
    gl = ax.gridlines(
        draw_labels=True,
        linewidth=0.4,
        linestyle=":",
        color="gray",
        xlocs=range(-180, 181, 10),  # longitude every 10°
        ylocs=range(0, 91, 10)       # latitude every 10°
    )
    
    # Hide top/right labels for cleaner map
    gl.right_labels = False
    gl.top_labels = False
    
    # Reduce font size
    gl.xlabel_style = {"size": 8}
    gl.ylabel_style = {"size": 8}
    
    # ----------------------------------------------------------
    # Plot obs (lon in 0–360)
    # ----------------------------------------------------------
    ax.scatter(lon, lat, s=1, alpha=0.7, transform=ccrs.PlateCarree())
    
    # Title
    ax.set_title(f"{sensor}  {cycle}\nSpatial Distribution (N={len(lat)})")

    # Save
    outpath = os.path.join(outdir, basename.replace(".pkl", ".png"))
    plt.tight_layout()
    plt.savefig(outpath, dpi=150)
    plt.close()
    print(f"[INFO] Saved: {outpath}")


# ---------------------------------------------------------
# Main
# ---------------------------------------------------------

def main():
    if len(sys.argv) < 3:
        print("Usage: python plot_conv_spatial_detail.py START_CYCLE END_CYCLE")
        sys.exit(1)

    start_cycle = sys.argv[1]
    end_cycle   = sys.argv[2]

    # Make output directory
    outdir = "figures_detail"
    os.makedirs(outdir, exist_ok=True)

    valid_cycles = cycle_range(start_cycle, end_cycle)

    # Load pickle files
    pkl_files = sorted(glob.glob("pickle_detail/*.pkl"))
    if not pkl_files:
        print("[WARN] No pickle_detail/*.pkl found")
        sys.exit(0)

    print(f"[INFO] Searching cycles from {start_cycle} to {end_cycle}")
    print(f"[INFO] Total pickle files: {len(pkl_files)}")

    count = 0
    for pkl_path in pkl_files:
        cycle = extract_cycle_from_filename(pkl_path)
        if cycle in valid_cycles:
            plot_spatial_distribution(pkl_path, outdir)
            count += 1

    print(f"[INFO] Completed. Plotted {count} files.")

if __name__ == "__main__":
    main()
