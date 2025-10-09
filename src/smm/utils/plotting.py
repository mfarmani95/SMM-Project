import matplotlib.pyplot as plt
import os
import numpy as np

def plot_results(da, fits, pos_inc, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 5))
    da.plot(ax=ax, label="Soil Moisture", marker=".", linestyle="None")

    def exp_model(t, A, B, C):
        return A * np.exp(-B * t) + C

    for fit in fits:
        seg = da.sel(time=slice(fit["start"], fit["end"]))
        t = (seg["time"].values.astype("datetime64[D]") - np.datetime64(fit["start"], "D")).astype(int)
        y = exp_model(t, fit["A"], fit["B"], fit["C"])
        ax.plot(seg["time"], y, "r--")

    for i in range(len(pos_inc["end"])):
        da.sel(time=slice(pos_inc["start"][i], pos_inc["end"][i])).plot(color="orange", marker=".")

    ax.legend()
    fig.savefig(os.path.join(output_dir, "SMM_plot.png"), dpi=300)
    plt.close(fig)

