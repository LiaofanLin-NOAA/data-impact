#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modernized Data Impact Plotter
Reads pickle files under ./pickle and outputs figures to ./figures_post.

Features:
 - Matches original numeric logic (including conv + conv_uv for Conventional)
 - Wider, cleaner figure layout
 - Right-aligned, comma-formatted summary text above plots
 - Darker dashed gridlines for clarity
 - CLI switch: --mode [each|total|both]
"""

import numpy as np
import matplotlib.pyplot as plt
import pickle
from pathlib import Path
import argparse
from tqdm import tqdm


# ==========================================================
#  Utility
# ==========================================================
def read_pickle(file_path):
    """Read a pickle file and return unpacked data."""
    with open(file_path, "rb") as f:
        return pickle.load(f)


# ==========================================================
#  Per-cycle Plot
# ==========================================================
def plot_cycle(
    datestr,
    all_sensor_type,
    all_sum_jo_diff,
    all_mean_jo_diff,
    all_assim_size,
    sate_sum_jo_diff,
    sate_ir_sum_jo_diff,
    conv_sum_jo_diff,
    sate_assim_size,
    sate_ir_assim_size,
    conv_assim_size,
    colors,
    outdir,
):
    """Plot and save one analysis cycle figure."""
    import matplotlib.gridspec as gridspec

    fig = plt.figure(figsize=(18, 8), constrained_layout=False)
    gs = gridspec.GridSpec(1, 3, width_ratios=[1, 1, 1], wspace=0.10)
    ax1 = plt.subplot(gs[0])
    ax2 = plt.subplot(gs[1], sharey=ax1)
    ax3 = plt.subplot(gs[2], sharey=ax1)

    # -------- Bar 1: Total Impact --------
    ax1.barh(range(len(all_sensor_type)), all_sum_jo_diff, color=colors)
    ax1.set_yticks(range(len(all_sensor_type)))
    ax1.set_yticklabels(all_sensor_type, fontsize=10)
    ax1.invert_yaxis()
    ax1.set_xlabel("Total Impact [Unitless]", fontsize=11)
    ax1.grid(True, linestyle="--", alpha=0.8, color="gray")

    # -------- Bar 2: Impact per Obs --------
    ax2.barh(range(len(all_sensor_type)), all_mean_jo_diff, color=colors)
    ax2.ticklabel_format(style="sci", axis="x", scilimits=(0, 0))
    ax2.set_xlabel("Impact Per Obs [Unitless]", fontsize=11)
    ax2.grid(True, linestyle="--", alpha=0.8, color="gray")
    plt.setp(ax2.get_yticklabels(), visible=False)

    # -------- Bar 3: Assim Obs Size --------
    ax3.barh(range(len(all_sensor_type)), all_assim_size, color=colors)
    ax3.ticklabel_format(style="sci", axis="x", scilimits=(0, 0))
    ax3.set_xlabel("Assim Obs Size", fontsize=11)
    ax3.grid(True, linestyle="--", alpha=0.8, color="gray")
    plt.setp(ax3.get_yticklabels(), visible=False)

    fmt = lambda x: f"{x:,.0f}"
    fig.suptitle(f"Date = {datestr}", fontsize=14, x=0.52, y=0.93)

    fig.text(0.36, 0.930,
             f"Total Impact, MW Satellite = {fmt(sum(sate_sum_jo_diff) - sum(sate_ir_sum_jo_diff))}",
             color="blue", fontsize=13, ha="right", va="bottom")
    fig.text(0.36, 0.907,
             f"Total Impact, IR Satellite = {fmt(sum(sate_ir_sum_jo_diff))}",
             color="red", fontsize=13, ha="right", va="bottom")
    fig.text(0.36, 0.884,
             f"Total Impact, Conventional = {fmt(sum(conv_sum_jo_diff))}",
             fontsize=13, ha="right", va="bottom")

    fig.text(0.90, 0.930,
             f"Total Assim, MW Satellite = {fmt(sum(sate_assim_size) - sum(sate_ir_assim_size))}",
             color="blue", fontsize=13, ha="right", va="bottom")
    fig.text(0.90, 0.907,
             f"Total Assim, IR Satellite = {fmt(sum(sate_ir_assim_size))}",
             color="red", fontsize=13, ha="right", va="bottom")
    fig.text(0.90, 0.884,
             f"Total Assim, Conventional = {fmt(sum(conv_assim_size))}",
             fontsize=13, ha="right", va="bottom")

    fig.tight_layout(rect=[0, 0, 1, 0.90])
    out_path = outdir / f"{datestr}-fsoi-proxy.png"
    fig.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


# ==========================================================
#  Total (Averaged) Plot
# ==========================================================
def plot_total_summary(
    case_str,
    datestr_len,
    all_sensor_type,
    alltime_sum_jo_diff,
    alltime_assim_size,
    alltime_sate_sum_jo_diff,
    alltime_sate_ir_sum_jo_diff,
    alltime_conv_sum_jo_diff,
    alltime_sate_assim_size,
    alltime_sate_ir_assim_size,
    alltime_conv_assim_size,
    colors,
    outdir,
):
    """Plot averaged-per-cycle total data impact."""
    import matplotlib.gridspec as gridspec

    fig = plt.figure(figsize=(18, 8), constrained_layout=False)
    gs = gridspec.GridSpec(1, 3, width_ratios=[1, 1, 1], wspace=0.10)
    ax1 = plt.subplot(gs[0])
    ax2 = plt.subplot(gs[1], sharey=ax1)
    ax3 = plt.subplot(gs[2], sharey=ax1)

    ax1.barh(range(len(all_sensor_type)), alltime_sum_jo_diff / datestr_len, color=colors)
    ax2.barh(range(len(all_sensor_type)), alltime_sum_jo_diff / alltime_assim_size, color=colors)
    ax3.barh(range(len(all_sensor_type)), alltime_assim_size / datestr_len, color=colors)

    for ax, label in zip(
        [ax1, ax2, ax3],
        ["Total Impact [Unitless]", "Impact Per Obs [Unitless]", "Assim Obs Size Per Cycle"],
    ):
        ax.set_xlabel(label, fontsize=11)
        ax.grid(True, linestyle="--", alpha=0.8, color="gray")
        ax.ticklabel_format(style="sci", axis="x", scilimits=(0, 0))
        ax.invert_yaxis()

    ax1.set_yticks(range(len(all_sensor_type)))
    ax1.set_yticklabels(all_sensor_type, fontsize=10)
    plt.setp(ax2.get_yticklabels(), visible=False)
    plt.setp(ax3.get_yticklabels(), visible=False)

    fmt = lambda x: f"{x:,.0f}"
    fig.suptitle(f"Cycle-Averaged Total Impact ({case_str})", fontsize=14, x=0.52, y=0.93)

    fig.text(0.36, 0.930,
             f"Avg Total Impact, MW Satellite = {fmt((sum(alltime_sate_sum_jo_diff) - sum(alltime_sate_ir_sum_jo_diff)) / datestr_len)}",
             color="blue", fontsize=13, ha="right", va="bottom")
    fig.text(0.36, 0.907,
             f"Avg Total Impact, IR Satellite = {fmt(sum(alltime_sate_ir_sum_jo_diff) / datestr_len)}",
             color="red", fontsize=13, ha="right", va="bottom")
    fig.text(0.36, 0.884,
             f"Avg Total Impact, Conventional = {fmt(sum(alltime_conv_sum_jo_diff) / datestr_len)}",
             fontsize=13, ha="right", va="bottom")

    fig.text(0.90, 0.930,
             f"Avg Assim, MW Satellite = {fmt((sum(alltime_sate_assim_size) - sum(alltime_sate_ir_assim_size)) / datestr_len)}",
             color="blue", fontsize=13, ha="right", va="bottom")
    fig.text(0.90, 0.907,
             f"Avg Assim, IR Satellite = {fmt(sum(alltime_sate_ir_assim_size) / datestr_len)}",
             color="red", fontsize=13, ha="right", va="bottom")
    fig.text(0.90, 0.884,
             f"Avg Assim, Conventional = {fmt(sum(alltime_conv_assim_size) / datestr_len)}",
             fontsize=13, ha="right", va="bottom")

    fig.tight_layout(rect=[0, 0, 1, 0.90])
    fig.savefig(outdir / "total-fsoi-proxy.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


# ==========================================================
#  Main Function
# ==========================================================
def main(case_str, mode="each"):
    base_dir = Path(__file__).resolve().parents[1]
    pickle_dir = base_dir / "pickle"
    fig_dir = base_dir / "figures_post" / case_str
    fig_dir.mkdir(parents=True, exist_ok=True)

    ir_index = [0, 1, 10, 11, 12, 13]
    mw_index = [2, 3, 4, 5, 6, 7, 8, 9, 14, 15, 16, 17]
    colors = ["red" if i in ir_index else "blue" if i in mw_index else "black" for i in range(26)]

    # Generate datetimes from 2024-09-25 06 UTC to 2024-09-30 23 UTC
    datestr_list = []
    for day in range(25, 31):              # 25 to 30 inclusive
        start_hour = 6 if day == 25 else 0
        end_hour = 24
        for h in range(start_hour, end_hour):
            datestr_list.append(f"202409{day:02d}{h:02d}")    

    # Data type information
    len_data_type, len_sate_data, len_conv_data = 26, 18, 8

    # Accumulators for total plot
    alltime_sum_jo_diff = np.zeros(len_data_type)
    alltime_assim_size = np.zeros(len_data_type)
    alltime_sate_sum_jo_diff = np.zeros(len_sate_data)
    alltime_sate_ir_sum_jo_diff = np.zeros(6)
    alltime_conv_sum_jo_diff = np.zeros(len_conv_data)
    alltime_sate_assim_size = np.zeros(len_sate_data)
    alltime_sate_ir_assim_size = np.zeros(6)
    alltime_conv_assim_size = np.zeros(len_conv_data)

    for d in tqdm(datestr_list, desc="Processing cycles"):
        datapath = "." if case_str == "full-domain" else "."
        date_dir = pickle_dir / datapath

        sate_file = date_dir / f"{d}_sate.pkl"
        conv_file = date_dir / f"{d}_conv.pkl"
        conv_uv_file = date_dir / f"{d}_conv_uv.pkl"

        if not (sate_file.exists() and conv_file.exists() and conv_uv_file.exists()):
            continue

        sate = read_pickle(sate_file)
        conv = read_pickle(conv_file)
        conv_uv = read_pickle(conv_uv_file)

        (
            sate_sensor_type, _, sate_assim_size, sate_mean_jo_diff, sate_sum_jo_diff, _
        ) = sate
        (
            conv_sensor_type, _, conv_assim_size, conv_mean_jo_diff, conv_sum_jo_diff, _
        ) = conv
        (
            convuv_sensor_type, _, convuv_assim_size, convuv_mean_jo_diff, convuv_sum_jo_diff, _
        ) = conv_uv

        sensor_type = sate_sensor_type + conv_sensor_type + convuv_sensor_type
        total_sum = np.concatenate([sate_sum_jo_diff, conv_sum_jo_diff, convuv_sum_jo_diff])
        mean_jo_diff = np.concatenate([sate_mean_jo_diff, conv_mean_jo_diff, convuv_mean_jo_diff])
        assim_size = np.concatenate([sate_assim_size, conv_assim_size, convuv_assim_size])

        # Conventional totals = 7 conv + 1 conv_uv (legacy logic)
        conv_total_sum = np.zeros(len_conv_data)
        conv_total_sum[0:len(conv_sum_jo_diff)] = conv_sum_jo_diff
        conv_total_sum[-1] = convuv_sum_jo_diff[-1]

        conv_total_assim = np.zeros(len_conv_data)
        conv_total_assim[0:len(conv_assim_size)] = conv_assim_size
        conv_total_assim[-1] = convuv_assim_size[-1]

        # -------- Per-cycle plots --------
        if mode in ["each", "both"]:
            plot_cycle(
                d,
                sensor_type,
                total_sum,
                mean_jo_diff,
                assim_size,
                sate_sum_jo_diff,
                sate_sum_jo_diff[ir_index],
                conv_total_sum,
                sate_assim_size,
                sate_assim_size[ir_index],
                conv_total_assim,
                colors,
                fig_dir,
            )

        # -------- Accumulate totals --------
        alltime_sum_jo_diff[0:len_sate_data] += sate_sum_jo_diff
        alltime_sum_jo_diff[len_sate_data:] += conv_total_sum
        alltime_assim_size[0:len_sate_data] += sate_assim_size
        alltime_assim_size[len_sate_data:] += conv_total_assim
        alltime_sate_sum_jo_diff += sate_sum_jo_diff
        alltime_sate_ir_sum_jo_diff += sate_sum_jo_diff[ir_index]
        alltime_conv_sum_jo_diff += conv_total_sum
        alltime_sate_assim_size += sate_assim_size
        alltime_sate_ir_assim_size += sate_assim_size[ir_index]
        alltime_conv_assim_size += conv_total_assim

    # -------- Total averaged plot --------
    if mode in ["total", "both"]:
        plot_total_summary(
            case_str,
            len(datestr_list),
            sensor_type,
            alltime_sum_jo_diff,
            alltime_assim_size,
            alltime_sate_sum_jo_diff,
            alltime_sate_ir_sum_jo_diff,
            alltime_conv_sum_jo_diff,
            alltime_sate_assim_size,
            alltime_sate_ir_assim_size,
            alltime_conv_assim_size,
            colors,
            fig_dir,
        )

    print(f"--> Figures saved to {fig_dir}")


# ==========================================================
#  CLI
# ==========================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate FSOI proxy plots from pickle data.")
    parser.add_argument("--case", choices=["full-domain", "sub-domain"], default="full-domain",
                        help="Case to process")
    parser.add_argument("--mode", choices=["each", "total", "both"], default="both",
                        help="Plot mode: 'each' = per-cycle only, 'total' = total only, 'both' = both types")
    args = parser.parse_args()

    main(args.case, mode=args.mode)
