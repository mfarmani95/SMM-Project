import os
import logging
import numpy as np
import matplotlib.pyplot as plt
from smm.utils.math_utils import exp_model

logger = logging.getLogger(__name__)

def plot_results(da, fits, pos_inc, output_dir):
    """
    Plot soil moisture time series, exponential fits (Tau_L),
    and short-term increments (Tau_S).

    Parameters
    ----------
    da : xarray.DataArray
        Soil moisture time series.
    fits : list[dict]
        List of exponential fit parameters (Tau_L).
    pos_inc : dict
        Positive increment metadata (Tau_S).
    output_dir : str
        Directory to save the figure.
    """
    logger.info(f"Starting plotting routine. Output dir: {output_dir}")
    try:
        os.makedirs(output_dir, exist_ok=True)
        logger.debug(f"Ensured output directory exists: {output_dir}")

        fig, ax = plt.subplots(figsize=(10, 5))
        da.plot(ax=ax, label="Soil Moisture", marker=".", linestyle="None")
        logger.debug(f"Plotted soil moisture series with {len(da)} points.")

        # --- Plot fits (Tau_L) ---
        tau_L_label_added = False
        for fit in fits:
            seg = da.sel(time=slice(fit["start"], fit["end"]))
            t = (
                seg["time"].values.astype("datetime64[D]")
                - np.datetime64(fit["start"], "D")
            ).astype(int)
            y = exp_model(t, fit["A"], fit["TAU_L"], fit["C"])

            if not tau_L_label_added:
                ax.plot(seg["time"], y, "r--", label="Tau_L")
                tau_L_label_added = True
            else:
                ax.plot(seg["time"], y, "r--")
        logger.info(f"Plotted {len(fits)} Tau_L fit segments.")

        # --- Plot pos increments (Tau_S) ---
        tau_S_label_added = False
        for i in range(len(pos_inc["end"])):
            segment = da.sel(time=slice(pos_inc["start"][i], pos_inc["end"][i]))
            if not tau_S_label_added:
                segment.plot(color="orange", marker=".", label="Tau_S")
                tau_S_label_added = True
            else:
                segment.plot(color="orange", marker=".")
        logger.info(f"Plotted {len(pos_inc['end'])} Tau_S increment segments.")

        # --- Finalize figure ---
        ax.set_title("Soil Moisture Memory Analysis")
        ax.legend()
        plot_path = os.path.join(output_dir, "SMM_plot.png")
        fig.savefig(plot_path, dpi=300, bbox_inches="tight")
        plt.close(fig)

        logger.info(f"✅ Plot successfully saved to {plot_path}")

    except Exception as e:
        logger.exception(f"❌ Failed to generate plot: {e}")
        raise
