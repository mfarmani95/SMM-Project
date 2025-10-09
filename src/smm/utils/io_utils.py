import os
import json
import logging
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

def save_ts_values(Ts_values, pos, output_dir):
    """
    Save Ts values and associated metadata (start, end, increment)
    to CSV and JSON with detailed logging.

    Parameters
    ----------
    Ts_values : list[float]
        Computed short-term soil moisture memory values.
    pos : dict
        Dictionary containing drydown event metadata with keys
        ['start', 'end', 'increment'].
    output_dir : str
        Directory to save the output files.

    Returns
    -------
    tuple[str, str]
        Paths to the saved CSV and JSON files.
    """
    logger.info(f"Saving Ts values with metadata to output directory: {output_dir}")
    
    try:
        os.makedirs(output_dir, exist_ok=True)
        logger.debug(f"Ensured output directory exists: {output_dir}")

        # Combine metadata with Ts values
        df = pd.DataFrame({
            "start": pos.get("start", []),
            "end": pos.get("end", []),
            "increment": pos.get("increment", []),
            "Ts": Ts_values
        })
        logger.debug(f"Constructed DataFrame with {len(df)} entries.")

        # ---- Save as CSV ----
        csv_path = os.path.join(output_dir, "Ts_values.csv")
        df.to_csv(csv_path, index=False)
        logger.info(f"✅ Ts values and metadata successfully saved as CSV: {csv_path}")
        logger.debug(f"CSV head preview:\n{df.head()}")

        # ---- Save as JSON ----
        json_data = {
            "events": [
                {
                    "start": str(s),
                    "end": str(e),
                    "increment": float(inc) if inc is not None else None,
                    "Ts": float(ts) if ts is not None else None
                }
                for s, e, inc, ts in zip(
                    pos.get("start", []),
                    pos.get("end", []),
                    pos.get("increment", []),
                    Ts_values
                )
            ]
        }

        json_path = os.path.join(output_dir, "Ts_values.json")
        with open(json_path, "w") as f:
            json.dump(json_data, f, indent=2)
        logger.info(f"✅ Ts values and metadata successfully saved as JSON: {json_path}")

        return csv_path, json_path

    except Exception as e:
        logger.exception(f"❌ Failed to save Ts values and metadata: {e}")
        raise


import yaml
from smm.dataloader import load_data
from smm.analyzer import SoilMoistureAnalyzer
from smm.utils.plotting import plot_results
from smm.utils.io_utils import save_ts_values

def SMM(config_file):
    with open(config_file, "r") as f:
        cfg = yaml.safe_load(f)

    da, prc = load_data(
        cfg["data"]["sm_file"],
        cfg["data"]["prcp_file"],
        cfg["data"]["var_sm"],
        cfg["data"]["var_prcp"],
        cfg["data"]["lat_index"],
        cfg["data"]["lon_index"]
    )

    threshold = cfg["parameters"]["threshold_factor"] * (da.max().item() - da.min().item())
    analyzer = SoilMoistureAnalyzer(
        da,
        threshold,
        cfg["parameters"]["min_length"],
        cfg["parameters"]["max_zeros"],
        cfg["parameters"]["max_consecutive_positives"],
        cfg["parameters"]["max_gap_days"],
        cfg["parameters"]["r2_threshold"],
        dim=cfg["parameters"]["dim"]
    )

    clean, drydowns, fits, pos_inc = analyzer.find_drydowns_and_fit()
    Ts_values = analyzer.short_term_timescale(pos_inc, cfg["parameters"]["thickness"], prc)

    if cfg["output"]["plot"]:
        plot_results(clean, fits, pos_inc, cfg["output"]["save_dir"])

    if cfg["output"].get("save_csv", True):
        save_ts_values(Ts_values,pos_inc, cfg["output"]["save_dir"])

    print("✅ Short-term timescales saved successfully.")




def save_tl_fits(fits_list, output_dir):
    """
    Save TL fitting parameters (a, b, c, r2) and start/end dates
    to CSV and JSON with logging.

    Parameters
    ----------
    fits_list : list[dict]
        List of dictionaries containing keys:
        ['start', 'end', 'a', 'b', 'c', 'r2'].
    output_dir : str
        Directory to save the output files.

    Returns
    -------
    tuple[str, str]
        Paths to the saved CSV and JSON files.
    """
    logger.info(f"Saving TL fit parameters to output directory: {output_dir}")
    try:
        os.makedirs(output_dir, exist_ok=True)
        logger.debug(f"Ensured output directory exists: {output_dir}")

        # Convert datetime64 and numpy types to native Python types
        clean_fits = []
        for f in fits_list:
            clean_fits.append({
                "start": str(f["start"]),
                "end": str(f["end"]),
                "a": float(f["A"]) if isinstance(f["A"], (np.floating, float)) else f["A"],
                "b": float(f["TAU_L"]) if isinstance(f["TAU_L"], (np.floating, float)) else f["TAU_L"],
                "c": float(f["C"]) if isinstance(f["C"], (np.floating, float)) else f["C"],
                "r2": float(f["r2"]) if isinstance(f["r2"], (np.floating, float)) else f["r2"]
            })

        # ---- Save as CSV ----
        df = pd.DataFrame(clean_fits)
        csv_path = os.path.join(output_dir, "TL_fits.csv")
        df.to_csv(csv_path, index=False)
        logger.info(f"✅ TL fit parameters successfully saved as CSV: {csv_path}")
        logger.debug(f"CSV head preview:\n{df.head()}")

        # ---- Save as JSON ----
        json_path = os.path.join(output_dir, "TL_fits.json")
        with open(json_path, "w") as f:
            json.dump({"fits": clean_fits}, f, indent=2)
        logger.info(f"✅ TL fit parameters successfully saved as JSON: {json_path}")

        return csv_path, json_path

    except Exception as e:
        logger.exception(f"❌ Failed to save TL fit parameters: {e}")
        raise