import yaml
import logging
from smm.dataloader import load_data
from smm.analyzer import SoilMoistureAnalyzer
from smm.utils.plotting import plot_results
from smm.utils.io_utils import save_ts_values, save_tl_fits

logger = logging.getLogger(__name__)

def SMM(config_file):
    """
    Run full Soil Moisture Memory (SMM) analysis pipeline.
    """
    logger.info(f"🚀 Starting SMM pipeline using config file: {config_file}")

    try:
        # --- Load configuration ---
        with open(config_file, "r") as f:
            cfg = yaml.safe_load(f)
        logger.debug(f"Configuration loaded successfully:\n{cfg}")

        # --- Load data with optional unit conversion ---
        logger.info("📥 Loading soil moisture and precipitation data...")
        da, prc = load_data(
            sm_file=cfg["data"]["sm_file"],
            prcp_file=cfg["data"]["prcp_file"],
            var_sm=cfg["data"]["var_sm"],
            var_prcp=cfg["data"]["var_prcp"],
            lat=cfg["data"]["lat"],
            lon=cfg["data"]["lon"],
            length_unit=cfg["parameters"].get("precip_length_unit"),
            time_unit=cfg["parameters"].get("precip_time_unit"),
            sm_timestep=cfg["parameters"].get("sm_timestep")
        )
        logger.info("✅ Data loaded successfully.")
        logger.debug(f"Soil moisture shape: {da.shape}, Precip shape: {prc.shape}")

        # --- Threshold calculation ---
        threshold = cfg["parameters"]["threshold_factor"] * (da.max().item() - da.min().item())
        logger.debug(f"Threshold computed: {threshold:.6f}")

        # --- Analyzer initialization ---
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
        logger.info("🧮 Analyzer initialized.")

        # --- Run drydown analysis ---
        clean, drydowns, fits, pos_inc = analyzer.find_drydowns_and_fit()
        logger.info(f"✅ Drydown detection complete: {len(drydowns)} events found, {len(fits)} fits.")
        if fits:
            logger.debug(f"Fit sample: {fits[0]}")

        # --- Compute Ts (short-term timescales) ---
        Ts_values = analyzer.short_term_timescale(
            pos_inc,
            cfg["parameters"]["thickness"],
            prc
        )
        logger.info(f"✅ Computed {len(Ts_values)} short-term timescale (Tau_S) values.")
        if Ts_values:
            logger.debug(f"Ts sample: {Ts_values[:5]}")

        # --- Plotting ---
        if cfg["output"].get("plot", True):
            logger.info("📊 Generating plot...")
            plot_results(clean, fits, pos_inc, cfg["output"]["save_dir"])
            logger.info("✅ Plot saved successfully.")

        # --- Save Ts values ---
        if cfg["output"].get("save_csv", True):
            logger.info("💾 Saving Ts values...")
            save_ts_values(Ts_values, pos_inc, cfg["output"]["save_dir"])
            logger.info("✅ Ts values saved successfully.")

        # --- Save TL fits ---
        if cfg["output"].get("save_csv", True):
            logger.info("💾 Saving TL fit parameters...")
            save_tl_fits(fits, cfg["output"]["save_dir"])
            logger.info("✅ TL fits saved successfully.")

        logger.info("🎉 SMM pipeline completed successfully.")

    except FileNotFoundError as e:
        logger.error(f"❌ File not found: {e.filename}")
        logger.exception(e)
        raise
    except Exception as e:
        logger.exception(f"❌ SMM pipeline failed: {e}")
        raise
