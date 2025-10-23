#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================
Data Impact Analysis – Conventional Scalar Observations
Author: Liaofan Lin
Created: 2024-05-24
Updated: 2025-10-14
Description:
  Computes Jo-diff (ΔJ_o) statistics for assimilated
  conventional (non-vector) observations.

  Features:
    - Uses shared plotting and saving utilities from di_common.py
    - Preserves original figure text layout and pickle format
    - Prints data-length summaries (total/assimilated/monitored/rejected)
    - Issues signed warnings for large or zero Jo-diff values
==============================================================
"""

import os
import sys
import numpy as np
from pyGSI.diags import Conventional
from di_common import plot_jo_histogram, save_legacy_pickle


def analyze_conv(yyyy, mm, dd, hh, data_path, domain_str="True"):
    cycle = f"{yyyy}{mm}{dd}{hh}"
    sensor_types = ["conv_fed", "conv_ps", "conv_pw", "conv_q", "conv_rw", "conv_sst", "conv_t"]

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
        diag_ges = Conventional(diag_ges_path)
        diag_anl = Conventional(diag_anl_path)

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
        count_assim = 0
        count_large = 0
        count_zero = 0
        warn_sample_limit = 10  # limit printed samples per sensor

        # --- Main observation loop ---
        for i in range(len(data_anl)):
            ges, anl = data_ges.iloc[i], data_anl.iloc[i]
            inv_err = anl["errinv_final"]
            if inv_err == 0:
                continue
            if int(ges.name[6]) != 1 or int(anl.name[6]) != 1:
                continue

            # --- Apply domain filter if specified ---
            anl_latitude = float(anl["latitude"])
            anl_longitude = float(anl["longitude"])
            if not eval(domain_str, {"anl_latitude": anl_latitude, "anl_longitude": anl_longitude}):
                continue

            jo_diff = (anl["omf_adjusted"] ** 2 - ges["omf_adjusted"] ** 2) * (inv_err ** 2)
            jo_diffs.append(jo_diff)
            inv_obs_errors.append(inv_err)
            count_assim += 1

            # --- Diagnostic Warnings ---
            if abs(jo_diff) > 25:
                count_large += 1
                if count_large <= warn_sample_limit:
                    print(f"[WARN] {sensor}: index {i} jo_diff={jo_diff:.3f} "
                          f"(|jo_diff| > 25, possible outlier)")
                    print(f"       anl_omf={anl['omf_adjusted']:.3f}, "
                          f"ges_omf={ges['omf_adjusted']:.3f}, inv_err={inv_err:.3f}")
            elif jo_diff == 0:
                count_zero += 1
                if count_zero <= warn_sample_limit:
                    print(f"[WARN] {sensor}: index {i} jo_diff == 0 "
                          "(check obs or inv_obs_err)")

        # --- Warning summary ---
        print(f"[INFO] {sensor}: |jo_diff|>25 count = {count_large}")
        print(f"[INFO] {sensor}: jo_diff == 0 count = {count_zero}")

        # --- Plot histogram (shared function) ---
        if count_assim > 0:
            plot_jo_histogram(sensor, yyyy, mm, dd, hh,
                              jo_diffs, inv_obs_errors,
                              count_assim, count_large, count_zero,
                              data_anl, cycle)

            # --- Save stats for this sensor ---
            final_total_size[ss] = len(data_anl)
            final_assim_size[ss] = count_assim
            final_mean_jo_diff[ss] = np.mean(jo_diffs)
            final_sum_jo_diff[ss] = np.sum(jo_diffs)
            final_max_abs_jo_diff[ss] = np.max(np.abs(jo_diffs))

    # --- Save results (shared function) ---
    save_legacy_pickle(sensor_types,
                       final_total_size,
                       final_assim_size,
                       final_mean_jo_diff,
                       final_sum_jo_diff,
                       final_max_abs_jo_diff,
                       cycle, label="conv")

    
if __name__ == "__main__":
    if len(sys.argv) < 6:
        sys.exit("Usage: di_conv.py YYYY MM DD HH DATAPATH [DOMAIN]")
    yyyy, mm, dd, hh, data_path = sys.argv[1:6]
    domain_str = sys.argv[6] if len(sys.argv) > 6 else "True"
    print(f"[INFO] Domain selection string: {domain_str}")
    analyze_conv(yyyy, mm, dd, hh, data_path, domain_str)

