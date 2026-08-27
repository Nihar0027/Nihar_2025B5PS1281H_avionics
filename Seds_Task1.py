import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from scipy.signal import savgol_filter

def load_data(filepath):
    """Read the CSV and force the depth column to be numeric.
    Any junk text (like '#VALUE!') becomes NaN (Not a Number)."""
    df = pd.read_csv(filepath)# this read the file .
    df["Depth (m)"] = pd.to_numeric(df["Depth (m)"], errors="coerce")#here the errors="coerce" makes the non numeric value as NaN.
    return df

def clean_data(df, window=5, threshold=80):
    depth = df["Depth (m)"].copy()

    rolling_median = depth.rolling(window=window, center=True, min_periods=1).median()#this is used to average the points for a certain interval .
    deviation = (depth - rolling_median).abs()
    is_outlier = deviation > threshold #this here is used for the error like at one point the y is in like -1000 so which is very high for two points so we consider it as a error 


    depth[is_outlier] = np.nan
    depth = depth.interpolate(method="linear", limit_direction="both")

    df["Depth (m)"] = depth
    df["Outlier"] = is_outlier  # keep a record of what was flagged, for the plot
    return df

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

def animate_plot(df, interval_ms=1000):


    time = df["Point"].values            # takes the values under  point from the csv.file
    raw_depth = df["Depth (m)"].values   # takes the values under depth from the csv.file
    smooth_depth = smooth_data(raw_depth)
    outlier_mask = df["Outlier"].values

    fig, ax = plt.subplots(figsize=(10, 6))# used for height and width of the graph

    raw_line, = ax.plot([], [], color="skyblue", linewidth=1, label="Cleaned raw depth") #plots the line from the given points of csv.file
    smooth_line, = ax.plot([], [], color="navy", linewidth=2, label="Smoothed depth")    #plots the line using the scipy library
    outlier_pts, = ax.plot([], [], "rx", markersize=8, label="Corrected sensor errors") #mentions the sensor error in the graph

    ax.set_xlim(time.min(), time.max())                         # here from line 55 to 61 are used to set the limits of x,label them and make the graph neater
    ax.set_ylim(raw_depth.min() - 20, raw_depth.max() + 20)
    ax.set_xlabel("Time (seconds)")
    ax.set_ylabel("Depth (m)")
    ax.set_title("Ship Depth-Time Graph — Sea Floor Detection")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend(loc="lower right")

    def update(frame):                                                    #used to reveal data progressively over time—drawing 
        #a raw data line, a smoothed trend line, and highlighted outlier points step-by-step up to the current frame.
        raw_line.set_data(time[: frame + 1], raw_depth[: frame + 1])
        smooth_line.set_data(time[: frame + 1], smooth_depth[: frame + 1])

        shown_outliers = outlier_mask[: frame + 1]
        outlier_pts.set_data(time[: frame + 1][shown_outliers], raw_depth[: frame + 1][shown_outliers])
        return raw_line, smooth_line, outlier_pts

    ani = animation.FuncAnimation(
        fig, update, frames=len(time), interval=interval_ms, blit=True, repeat=False
    )
    plt.tight_layout()
    plt.show() # used to show the graph
    return ani

if __name__ == "__main__":
    DATA_FILE = "Depth Data.csv"

    df = load_data(DATA_FILE)
    df = clean_data(df)
    animate_plot(df, interval_ms=1000) # the time interval is in 1000 cuz it considers in milli seconds so 1000ms=1sec