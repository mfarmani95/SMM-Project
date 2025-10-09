import numpy as np
from scipy.optimize import curve_fit

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

    @staticmethod
    def _exp_model(t, A, b, C):
        return A * np.exp(-b * t) + C

    def _fit_exponential_decay(self, drydowns):
        results = []
        for start, end in drydowns:
            seg = self.da.sel({self.dim: slice(start, end)})
            tdays = ((seg[self.dim].values.astype("datetime64[D]") - np.datetime64(start, "D")).astype(int))
            y = seg.values
            bounds = ([0, 0, self.da.min().item()], [np.inf, np.inf, np.inf])
            ini = [y[0] - y[-1], 0.1, y[-1]]
            try:
                popt, _ = curve_fit(self._exp_model, tdays, y, p0=ini, bounds=bounds)
                A, B, C = popt
                y_pred = self._exp_model(tdays, A, B, C)
                ss_res = np.sum((y - y_pred) ** 2)
                ss_tot = np.sum((y - y.mean()) ** 2)
                r2 = 1 - ss_res / ss_tot if ss_tot > 0 else np.nan
            except Exception:
                A = B = C = r2 = np.nan

            results.append({
                "start": start, "end": end,
                "A": A, "B": B, "C": C, "r2": r2
            })
        return results

    def find_drydowns_and_fit(self):
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
        fits = self._fit_exponential_decay(filtered)
        drydowns = [(s, e) for (s, e), f in zip(filtered, fits) if f["r2"] >= self.r2_threshold]
        pos_inc = self._find_positive_increments(drydowns)
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
        Ts_list = []
        for s, e, inc in zip(pos_inc["start"], pos_inc["end"], pos_inc["increment"]):
            dt = (e - s) / np.timedelta64(1, "D") + 1
            PRCP = prc.sel({self.dim: slice(s, e)}).mean(dim=self.dim).item()
            FP = (thickness * inc) / PRCP
            Ts = -(dt / 2) / np.log(FP)
            Ts_list.append(Ts)
        return Ts_list

