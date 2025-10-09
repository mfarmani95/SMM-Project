import numpy as np
import logging
from scipy.optimize import curve_fit
from smm.utils.math_utils import exp_model  # ✅ use shared function

logger = logging.getLogger(__name__)

class SoilMoistureAnalyzer:
    def __init__(self, da, threshold, min_length, max_zeros,
                 max_consecutive_positives, max_gap_days, r2_threshold, dim="time"):
        self.da = da.dropna(dim=dim, how="any")
        self.threshold = threshold
        self.min_length = min_length
        self.max_zeros = max_zeros
        self.max_consecutive_positives = max_consecutive_positives
        self.max_gap_days = max_gap_days
        self.r2_threshold = r2_threshold
        self.dim = dim

        logger.info("🧮 SoilMoistureAnalyzer initialized")
        logger.debug(
            f"threshold={threshold}, min_length={min_length}, "
            f"max_zeros={max_zeros}, max_pos={max_consecutive_positives}, "
            f"max_gap_days={max_gap_days}, r2_threshold={r2_threshold}, dim={dim}"
        )

    def _fit_exponential_decay(self, drydowns):
        results = []
        logger.info(f"📉 Fitting exponential decay to {len(drydowns)} drydowns...")

        for start, end in drydowns:
            seg = self.da.sel({self.dim: slice(start, end)})
            tdays = ((seg[self.dim].values.astype("datetime64[D]") - np.datetime64(start, "D")).astype(int))
            y = seg.values

            bounds = ([0, 0, self.da.min().item()], [np.inf, np.inf, np.inf])
            ini = [y[0] - y[-1], 0.1, y[-1]]

            try:
                popt, _ = curve_fit(exp_model, tdays, y, p0=ini, bounds=bounds)
                A, B, C = popt
                y_pred = exp_model(tdays, A, B, C)

                ss_res = np.sum((y - y_pred) ** 2)
                ss_tot = np.sum((y - y.mean()) ** 2)
                r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan

                logger.debug(f"Fit success [{start} → {end}]: A={A:.4f}, B={B:.4f}, C={C:.4f}, R²={r2:.3f}")

            except Exception as e:
                logger.warning(f"⚠️ Fit failed for drydown [{start} → {end}]: {e}")
                A = B = C = r2 = np.nan

            results.append({
                "start": start, "end": end,
                "A": A, "TAU_L": B, "C": C, "r2": r2
            })

        logger.info(f"✅ Finished fitting. {sum(np.isfinite([f['r2'] for f in results]))} successful fits.")
        return results

    def find_drydowns_and_fit(self):
        logger.info("🔎 Detecting drydowns...")
        times = self.da[self.dim].values
        sm = self.da.values
        dvals = np.diff(sm)
        small_pos = (dvals > 0) & (dvals < self.threshold)

        raw = []
        start = None
        zero_cnt = pos_cnt = 0
        prev_t = None

        for i, delta in enumerate(dvals):
            t0, t1 = times[i], times[i + 1]
            if delta < 0:
                if start is None:
                    start = t0
                elif (t1 - prev_t) > np.timedelta64(self.max_gap_days, "D"):
                    raw.append((start, prev_t))
                    start = t1
                zero_cnt = pos_cnt = 0
            elif delta == 0 and start is not None:
                zero_cnt += 1
                if zero_cnt > self.max_zeros:
                    raw.append((start, prev_t))
                    start = None
            elif small_pos[i] and start is not None:
                pos_cnt += 1
                if pos_cnt > self.max_consecutive_positives:
                    raw.append((start, prev_t))
                    start = None
            else:
                if start is not None:
                    raw.append((start, prev_t))
                    start = None
            prev_t = t1

        if start is not None:
            raw.append((start, prev_t))

        filtered = [(s, e) for s, e in raw if self.da.sel({self.dim: slice(s, e)}).size >= self.min_length]
        logger.info(f"✅ Found {len(filtered)} drydowns (after min length filtering).")

        fits = self._fit_exponential_decay(filtered)
        drydowns = [(s, e) for (s, e), f in zip(filtered, fits) if f["r2"] >= self.r2_threshold]
        logger.info(f"📊 {len(drydowns)} fits passed R² threshold ({self.r2_threshold}).")

        pos_inc = self._find_positive_increments(drydowns)
        logger.info(f"🌧️ Detected {len(pos_inc['start'])} positive increments (Tau_S candidates).")

        return self.da, drydowns, fits, pos_inc

    def _find_positive_increments(self, drydowns):
        times = self.da[self.dim].values
        sm = self.da.values
        dvals = np.diff(sm)
        pos_idx = np.where(dvals > 0)[0]
        dry_idx = set()

        for s, e in drydowns:
            mask = (times[:-1] >= s) & (times[1:] <= e)
            dry_idx |= set(np.nonzero(mask)[0])

        pos_idx = [i for i in pos_idx if i not in dry_idx]
        starts = [times[i] for i in pos_idx]
        ends = [times[i + 1] for i in pos_idx]
        incs = [float(dvals[i]) for i in pos_idx]

        return {"start": starts, "end": ends, "increment": incs}

    def short_term_timescale(self, pos_inc, thickness, prc):
        logger.info("⏳ Calculating short-term timescales (Tau_S)...")
        Ts_list = []

        for s, e, inc in zip(pos_inc["start"], pos_inc["end"], pos_inc["increment"]):
            dt = (e - s) / np.timedelta64(1, "D") + 1
            PRCP = prc.sel({self.dim: slice(s, e)}).mean(dim=self.dim).item()

            if PRCP <= 0:
                logger.warning(f"⚠️ Skipping increment [{s} → {e}] due to zero/negative precipitation.")
                continue

            FP = (thickness * inc) / PRCP
            try:
                Ts = -(dt / 2) / np.log(FP)
                Ts_list.append(Ts)
                logger.debug(f"Tau_S for [{s} → {e}] = {Ts:.3f}")
            except Exception as ex:
                logger.warning(f"⚠️ Failed to compute Tau_S for [{s} → {e}]: {ex}")

        logger.info(f"✅ Computed {len(Ts_list)} Tau_S values.")
        return Ts_list
