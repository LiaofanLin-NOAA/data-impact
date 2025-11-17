#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
==============================================================
Data Impact Analysis – Conventional U/V Wind Observations
Author: Liaofan Lin
Created: 2024-05-24
Updated: 2025-10-14
Description:
  Computes Jo-diff (ΔJ_o) statistics for assimilated
  conventional wind vector observations (U/V components).

  Notes:
    Each record includes both U and V components.  Each component
    contributes one independent Jo-diff value (two per record).
==============================================================
"""

import os
import sys
import numpy as np
from pyGSI.diags import Conventional
from di_common import plot_jo_histogram, save_legacy_pickle
import pickle


def analyze_conv_uv(yyyy, mm, dd, hh, data_path, domain_str="True", save_detail=False):
    cycle = f"{yyyy}{mm}{dd}{hh}"
    sensor_types = ["conv_uv"]

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
        total_count = len(data_ges) * 2
        assim_count = len(data_ges_qc["assimilated"]) * 2
        monitor_count = len(data_ges_qc["monitored"]) * 2
        reject_count = len(data_ges_qc["rejected"]) * 2

        print(f"  Length of data, total: {total_count}")
        print(f"  Length of data that were assimilated: {assim_count}")
        print(f"  Length of data that were monitored: {monitor_count}")
        print(f"  Length of data that were rejected: {reject_count}")

        # --- Initialize accumulators ---
        jo_diffs, inv_obs_errors = [], []
        sensor_lon, sensor_lat = [], []
        sensor_press = []
        sensor_obstype = []        
        
        count_assim = 0
        count_large = 0
        count_zero = 0
        warn_sample_limit = 10  # limit printed samples per sensor

        # --- Main observation loop ---
        for i in range(len(data_anl)):
            # From the pyGSI/diag.py: 
            #indices = ['Station_ID', 'Observation_Class', 'Observation_Type',
            #           'Observation_Subtype', 'Pressure', 'Height',
            #           'Analysis_Use_Flag']         
            
            ges, anl = data_ges.iloc[i], data_anl.iloc[i]
            inv_err = anl["errinv_final"]
            if inv_err == 0:
                continue
            if int(ges.name[6]) != 1 or int(anl.name[6]) != 1:
                continue

            # --- Apply domain filter if specified ---
            anl_latitude  = float(anl["latitude"])
            anl_longitude = float(anl["longitude"])
            if not eval(domain_str, {"anl_latitude": anl_latitude, "anl_longitude": anl_longitude}):
                continue
                
            # --- Compute Jo-diff for each component separately ---
            jo_diff_u = (anl["u_omf_adjusted"] ** 2 - ges["u_omf_adjusted"] ** 2) * (inv_err ** 2)
            jo_diff_v = (anl["v_omf_adjusted"] ** 2 - ges["v_omf_adjusted"] ** 2) * (inv_err ** 2)

            jo_diffs.extend([jo_diff_u, jo_diff_v])
            inv_obs_errors.extend([inv_err, inv_err])
            count_assim += 2  # two scalar observations per record

            # --- Collect detailed information ---
            sensor_lat.extend([anl_latitude, anl_latitude])
            sensor_lon.extend([anl_longitude, anl_longitude])
            sensor_press.extend([anl.name[4], anl.name[4]])   # Pressure
            sensor_obstype.extend([anl.name[2], anl.name[2]]) # Observation type
            
            # --- Diagnostic Warnings (per component) ---
            for comp_name, jo_val in zip(["U", "V"], [jo_diff_u, jo_diff_v]):
                if abs(jo_val) > 25:
                    count_large += 1
                    if count_large <= warn_sample_limit:
                        print(f"[WARN] {sensor}: index {i}, comp={comp_name} jo_diff={jo_val:.3f} "
                              f"(|jo_diff| > 25, possible outlier)")
                        print(f"       anl_{comp_name.lower()}={anl[f'{comp_name.lower()}_omf_adjusted']:.3f}, "
                              f"ges_{comp_name.lower()}={ges[f'{comp_name.lower()}_omf_adjusted']:.3f}, "
                              f"inv_err={inv_err:.3f}")
                elif jo_val == 0:
                    count_zero += 1
                    if count_zero <= warn_sample_limit:
                        print(f"[WARN] {sensor}: index {i}, comp={comp_name} jo_diff == 0 "
                              "(check obs or inv_obs_err)")

        # --- Warning summary ---
        print(f"[INFO] {sensor}: |jo_diff|>25 count = {count_large}")
        print(f"[INFO] {sensor}: jo_diff == 0 count = {count_zero}")

        # --- Save detailed info, plot histogram, and save overall stat ---
        if count_assim > 0:

            # --- Save detailed per-point data to pickle_detail/ ---
            if save_detail:            
                
                detail_dir  = "pickle_detail"
                detail_file = os.path.join(detail_dir, f"{cycle}_{sensor}_detail.pkl")

                detail_dict = {
                    "jo_diff": np.array(jo_diffs),
                    "inv_obs_errors": np.array(inv_obs_errors),
                    "latitude": np.array(sensor_lat),
                    "longitude": np.array(sensor_lon),
                    "pressure": np.array(sensor_press),         
                    "observation_type": np.array(sensor_obstype) 
                }

                with open(detail_file, "wb") as f:
                    pickle.dump(detail_dict, f, protocol=pickle.HIGHEST_PROTOCOL)

            # --- Continue with your normal workflow ---                        
            plot_jo_histogram(sensor, yyyy, mm, dd, hh,
                              jo_diffs, inv_obs_errors,
                              count_assim, count_large, count_zero,
                              data_anl, cycle)

            # --- Save stats for this sensor ---
            final_total_size[ss] = total_count
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
                       cycle, label="conv_uv")


if __name__ == "__main__":
    if len(sys.argv) < 6:
        sys.exit("Usage: di_conv.py YYYY MM DD HH DATAPATH [DOMAIN] [SAVE_DETAIL]")

    yyyy, mm, dd, hh, data_path = sys.argv[1:6]
    domain_str  = sys.argv[6] if len(sys.argv) > 6 else "True"
    save_detail = sys.argv[7].lower() in ["true"] if len(sys.argv) > 7 else False

    print(f"[INFO] Domain selection string: {domain_str}")
    print(f"[INFO] Save detailed pickle: {save_detail}")
    analyze_conv_uv(yyyy, mm, dd, hh, data_path, domain_str, save_detail)
