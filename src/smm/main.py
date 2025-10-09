import yaml
from smm.dataloader import load_data
from smm.analyzer import SoilMoistureAnalyzer
from smm.utils.plotting import plot_results
from smm.utils.io_utils import save_ts_values

def main(config_file):
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
        save_ts_values(Ts_values, cfg["output"]["save_dir"])

    print("✅ Short-term timescales saved successfully.")

