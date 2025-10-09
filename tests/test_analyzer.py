import numpy as np
import xarray as xr
from smm.analyzer import SoilMoistureAnalyzer

def make_fake_data():
    """Generate a small fake time series for testing."""
    time = np.arange('2000-01', '2000-02', dtype='datetime64[D]')
    sm = np.linspace(0.3, 0.1, len(time))  # simple decreasing trend
    da = xr.DataArray(
        sm,
        dims=["time"],
        coords={"time": time},
        name="soil_moisture"
    )
    return da

def test_drydown_detection():
    da = make_fake_data()
    analyzer = SoilMoistureAnalyzer(
        da,
        threshold=0.01,
        min_length=3,
        max_zeros=0,
        max_consecutive_positives=1,
        max_gap_days=6,
        r2_threshold=0.0,
        dim="time"
    )
    clean, drydowns, fits, pos_inc = analyzer.find_drydowns_and_fit()
    assert len(drydowns) > 0, "No drydowns detected in simple decreasing series"
    assert all(fit["r2"] >= 0 for fit in fits), "R² values should be valid numbers"

