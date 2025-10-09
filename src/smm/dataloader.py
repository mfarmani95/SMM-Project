import xarray as xr
import pandas as pd
import numpy as np

def load_data(sm_file, prcp_file, var_sm, var_prcp, lat_idx, lon_idx):
    """
    Load soil moisture and precipitation data for a specific point.
    Converts precipitation to m/day.
    """
    df = xr.open_dataset(sm_file, decode_times=False)
    prcp = xr.open_dataset(prcp_file, decode_times=False)

    units = df[var_sm].time.attrs["units"]
    origin = np.datetime64(pd.to_datetime(units.split("since")[1].strip()))
    da = df[var_sm].assign_coords(time=origin + df[var_sm]["time"].values.astype("timedelta64[D]"))
    da = da.isel(lat=lat_idx, lon=lon_idx)

    prc = prcp[var_prcp].isel(lat=lat_idx, lon=lon_idx)
    prc["time"] = da["time"].values

    # convert mm/s to m/day
    prc = prc * 3600 * 24 / 1000
    return da, prc

