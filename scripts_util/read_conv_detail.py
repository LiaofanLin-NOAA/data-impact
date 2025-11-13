#!/usr/bin/env python3
import pickle
import sys
import numpy as np

def read_conv_detail(pkl_path):
    # --- Load pickle ---
    with open(pkl_path, "rb") as f:
        data = pickle.load(f)

    # --- Extract arrays ---
    jo_diff = data["jo_diff"]
    inv_err = data["inv_obs_errors"]
    lat = data["latitude"]
    lon = data["longitude"]
    press = data["pressure"]
    obstype = data["observation_type"]

    # --- Number of rows to show ---
    n_show = min(10, len(jo_diff))

    print(f"\n[INFO] File: {pkl_path}")
    print(f"[INFO] Total points: {len(jo_diff)}")
    print(f"[INFO] Showing first {n_show} rows:\n")

    # --- Print header ---
    print(f"{'Index':>5}  {'Lat':>8}  {'Lon':>9}  {'Press':>8}  {'ObsType':>10}  {'Jo_diff':>12}  {'InvErr':>8}")
    print("-" * 70)

    # --- Print rows ---
    for i in range(n_show):
        print(f"{i:5d}  "
              f"{lat[i]:8.3f}  "
              f"{lon[i]:9.3f}  "
              f"{press[i]:8.1f}  "
              f"{str(obstype[i]):>10}  "
              f"{jo_diff[i]:12.4f}  "
              f"{inv_err[i]:8.4f}")

    print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("Usage: read_conv_detail.py <detail_pickle_file.pkl>")

    pkl_path = sys.argv[1]
    read_conv_detail(pkl_path)

