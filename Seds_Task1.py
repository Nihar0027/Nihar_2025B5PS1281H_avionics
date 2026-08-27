"""
Task 1: Finding the Sea Floor
------------------------------
Reads depth-sensor data, cleans corrupted/erratic readings, smooths noise,
and displays an animated depth-vs-time graph (one new point per second).
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.signal import savgol_filter


# ---------------------------------------------------------
# 1. GRAB THE DATA
# ---------------------------------------------------------
def load_data(filepath):
    """Read the CSV and force the depth column to be numeric.
    Any junk text (like '#VALUE!') becomes NaN (Not a Number)."""
    df = pd.read_csv(filepath)
    df["Depth (m)"] = pd.to_numeric(df["Depth (m)"], errors="coerce")
    return df


# ---------------------------------------------------------
# 2. CLEAN THE DATA (handle erratic / corrupted readings)
# ---------------------------------------------------------
def clean_data(df, window=5, threshold=80):
    """
    Detects two kinds of bad readings:
      a) Non-numeric junk (already turned into NaN by load_data)
      b) Sudden spikes/dropouts that don't fit the surrounding trend

    Method: compare each point to the ROLLING MEDIAN of its neighbours.
    If a point is too far off (> threshold metres) from that local median,
    it's flagged as an outlier and replaced with NaN, then INTERPOLATED
    (filled in using the values on either side).
    """
    depth = df["Depth (m)"].copy()

    rolling_median = depth.rolling(window=window, center=True, min_periods=1).median()
    deviation = (depth - rolling_median).abs()
    is_outlier = deviation > threshold

    depth[is_outlier] = np.nan
    depth = depth.interpolate(method="linear", limit_direction="both")

    df["Depth (m)"] = depth
    df["Outlier"] = is_outlier  # keep a record of what was flagged, for the plot
    return df


# ---------------------------------------------------------
# 3. SMOOTH THE DATA (reduce random sensor noise)
# ---------------------------------------------------------
def smooth_data(depth_values, window=11, polyorder=2):
    """
    Savitzky-Golay filter: fits a small polynomial over a sliding window
    of points and uses it to smooth the curve, without flattening real
    trends the way a simple average would.
    """
    if window >= len(depth_values):
        window = len(depth_values) - 1 if len(depth_values) % 2 == 0 else len(depth_values)
    if window % 2 == 0:
        window += 1  # window length must be odd
    return savgol_filter(depth_values, window_length=window, polyorder=polyorder)


# ---------------------------------------------------------
# 4. ANIMATE THE GRAPH
# ---------------------------------------------------------
def animate_plot(df, interval_ms=1000):
    """Plots one new data point every second (interval_ms), showing both
    the cleaned raw signal and the smoothed signal, plus the flagged
    outliers as red markers."""

    time = df["Point"].values
    raw_depth = df["Depth (m)"].values
    smooth_depth = smooth_data(raw_depth)
    outlier_mask = df["Outlier"].values

    fig, ax = plt.subplots(figsize=(10, 6))

    raw_line, = ax.plot([], [], color="skyblue", linewidth=1, label="Cleaned raw depth")
    smooth_line, = ax.plot([], [], color="navy", linewidth=2, label="Smoothed depth")
    outlier_pts, = ax.plot([], [], "rx", markersize=8, label="Corrected sensor errors")

    ax.set_xlim(time.min(), time.max())
    ax.set_ylim(raw_depth.min() - 20, raw_depth.max() + 20)
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Depth (m)")
    ax.set_title("Ship Depth-Time Graph — Sea Floor Detection")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="lower right")

    def update(frame):
        raw_line.set_data(time[: frame + 1], raw_depth[: frame + 1])
        smooth_line.set_data(time[: frame + 1], smooth_depth[: frame + 1])

        shown_outliers = outlier_mask[: frame + 1]
        outlier_pts.set_data(time[: frame + 1][shown_outliers], raw_depth[: frame + 1][shown_outliers])
        return raw_line, smooth_line, outlier_pts

    ani = animation.FuncAnimation(
        fig, update, frames=len(time), interval=interval_ms, blit=True, repeat=False
    )
    plt.tight_layout()
    plt.show()
    return ani


# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------
if __name__ == "__main__":
    DATA_FILE = "Depth Data.csv"

    df = load_data(DATA_FILE)
    df = clean_data(df)

    # NOTE: interval_ms=1000 replays data in true real time (1 pt/sec, matches
    # the sensor's real recording rate). Lower it (e.g. 50) for a fast preview
    # while testing.
    animate_plot(df, interval_ms=1000)