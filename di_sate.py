#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================
Data Impact Analysis – Satellite Radiance Observations
Author: Liaofan Lin
Created: 2024-05-24
Updated: 2025-10-14
Description:
  Computes Jo-diff (ΔJ_o) statistics for assimilated
  satellite radiance data (e.g., ABI, CrIS, ATMS).

  Features:
    - Compatible with legacy pyGSI column names
    - Uses shared plotting/saving utilities from di_common.py
    - Preserves figure text layout and pickle format
    - Easily select sensors via comment toggling
    - Optionally saves per-channel/lat/lon pickle vectors
==============================================================
"""

import os
import sys
import numpy as np
import pickle
from pyGSI.diags import Radiance
from di_common import plot_jo_histogram, save_legacy_pickle


def analyze_sate(yyyy, mm, dd, hh, data_path, domain_str="True", save_channel_info=False):
    cycle = f"{yyyy}{mm}{dd}{hh}"

    # ------------------------------------------------------------
    # Choose sensors: comment/uncomment as needed
    # ------------------------------------------------------------
    sensor_types = [
        'abi_g16','abi_g18','amsua_metop-b','amsua_metop-c','amsua_n15',
        'amsua_n18','amsua_n19','atms_n20','atms_n21','atms_npp',
        'cris-fsr_n20','cris-fsr_n21','iasi_metop-b','iasi_metop-c',
        'mhs_metop-b','mhs_metop-c','mhs_n19','ssmis_f17'
    ]
    #sensor_types = ['abi_g16']

    n_sensor = len(sensor_types)
    final_total_size = np.zeros(n_sensor)
    final_assim_size = np.zeros(n_sensor)
    final_mean_jo_diff = np.zeros(n_sensor)
    final_sum_jo_diff = np.zeros(n_sensor)
    final_max_abs_jo_diff = np.zeros(n_sensor)

    for ss, sensor in enumerate(sensor_types):
        file_prefix = os.path.join(data_path, hh)
        diag_ges_path = f"{file_prefix}/diag_{sensor}_ges.{cycle}.nc4"
        diag_anl_path = f"{file_prefix}/diag_{sensor}_anl.{cycle}.nc4"

        if not os.path.exists(diag_ges_path):
            print(f"[WARN] Missing file for {sensor}: {diag_ges_path}")
            continue

        print(f"=== Processing {sensor} ===")

        # --- Load diagnostics ---
        diag_ges = Radiance(diag_ges_path)
        diag_anl = Radiance(diag_anl_path)

        data_ges = diag_ges.get_data()
        data_anl = diag_anl.get_data()
        data_ges_qc = diag_ges.get_data(analysis_use=True)

        # --- Data length summary ---
        print(f"  Length of data, total: {len(data_ges)}")
        print(f"  Length of data that were assimilated: {len(data_ges_qc['assimilated'])}")
        print(f"  Length of data that were monitored: {len(data_ges_qc['monitored'])}")
        print(f"  Length of data that were rejected: {len(data_ges_qc['rejected'])}")

        # --- Initialize accumulators ---
        jo_diffs, inv_obs_errors = [], []
        list_channel, list_latitude, list_longitude = [], [], []
        count_assim = 0
        count_large = 0
        count_zero = 0
        warn_sample_limit = 10  # limit printed samples per sensor

        # --- Observation loop ---
        for i in range(len(data_anl)):
            ges_series = data_ges.iloc[i]
            anl_series = data_anl.iloc[i]

            ges_qc_flag = ges_series.name[1]
            anl_qc_flag = anl_series.name[1]
            ges_omf = ges_series.get("omf_adjusted", np.nan)
            anl_omf = anl_series.get("omf_adjusted", np.nan)
            inv_err = anl_series.get("inverse_observation_error", np.nan)
            if np.isnan(inv_err) or inv_err == 0:
                continue

            # --- Apply domain filter if specified ---
            anl_latitude  = anl_series.get("latitude", np.nan)
            anl_longitude = anl_series.get("longitude", np.nan)
            if not eval(domain_str, {"anl_latitude": anl_latitude, "anl_longitude": anl_longitude}):
                continue

            # Compute Jo-diff
            jo_diff = (anl_omf**2 - ges_omf**2) * (inv_err**2)

            if i % 200000 == 0:
                print(f"  Processing i = {i}")

            # Assimilated data: QC == 0 for both
            if (int(ges_qc_flag) == 0) and (int(anl_qc_flag) == 0) and (inv_err != 0):
                count_assim += 1
                jo_diffs.append(jo_diff)
                inv_obs_errors.append(inv_err)

                list_channel.append(anl_series.get("channel_index", np.nan))
                list_latitude.append(anl_series.get("latitude", np.nan))
                list_longitude.append(anl_series.get("longitude", np.nan))

                # --- Diagnostic Warnings ---
                if abs(jo_diff) > 25:
                    count_large += 1
                    if count_large <= warn_sample_limit:
                        print(f"[WARN] {sensor}: index {i} jo_diff={jo_diff:.3f} "
                              f"(|jo_diff| > 25, possible outlier)")
                        print(f"       anl_omf={anl_omf:.3f}, ges_omf={ges_omf:.3f}, inv_err={inv_err:.3f}")
                elif jo_diff == 0:
                    count_zero += 1
                    if count_zero <= warn_sample_limit:
                        print(f"[WARN] {sensor}: index {i} jo_diff == 0 (check obs or inv_obs_err)")

        # --- Warning summary ---
        print(f"[INFO] {sensor}: |jo_diff|>25 count = {count_large}")
        print(f"[INFO] {sensor}: jo_diff == 0 count = {count_zero}")

        # --- Optional per-channel metadata pickle ---
        if save_channel_info and count_assim > 0:
            os.makedirs("./pickle", exist_ok=True)
            filename = f"./pickle/{cycle}_sate_channel_{sensor}.pkl"
            with open(filename, "wb") as f:
                pickle.dump([sensor, list_channel, list_latitude, list_longitude], f)
            print(f"[SAVE] Channel metadata: {filename}")

        # --- Plot histogram (shared) ---
        if count_assim > 0:
            plot_jo_histogram(sensor, yyyy, mm, dd, hh,
                              jo_diffs, inv_obs_errors,
                              count_assim, count_large, count_zero,
                              data_anl, cycle)

            # --- Save stats ---
            final_total_size[ss] = len(data_anl)
            final_assim_size[ss] = count_assim
            final_mean_jo_diff[ss] = np.mean(jo_diffs)
            final_sum_jo_diff[ss] = np.sum(jo_diffs)
            final_max_abs_jo_diff[ss] = np.max(np.abs(jo_diffs))

    # --- Save summary pickle ---
    save_legacy_pickle(sensor_types,
                       final_total_size,
                       final_assim_size,
                       final_mean_jo_diff,
                       final_sum_jo_diff,
                       final_max_abs_jo_diff,
                       cycle, label="sate")


if __name__ == "__main__":
    if len(sys.argv) < 6:
        sys.exit("Usage: di_conv.py YYYY MM DD HH DATAPATH [DOMAIN]")
    yyyy, mm, dd, hh, data_path = sys.argv[1:6]
    domain_str = sys.argv[6] if len(sys.argv) > 6 else "True"
    print(f"[INFO] Domain selection string: {domain_str}")
    analyze_sate(yyyy, mm, dd, hh, data_path, domain_str)
