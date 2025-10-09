import xarray as xr
import pandas as pd
import numpy as np
import logging
from smm.utils.unit_utils import PrecipConverter

logger = logging.getLogger(__name__)

def load_data(
    sm_file,
    prcp_file,
    var_sm,
    var_prcp,
    lat,
    lon,
    length_unit=None,
    time_unit=None,
    sm_timestep=None
):
    """
    Load soil moisture and precipitation data for a specific point,
    optionally converting precipitation units to match soil moisture timestep.

    Parameters
    ----------
    sm_file : str
        Path to soil moisture NetCDF file.
    prcp_file : str
        Path to precipitation NetCDF file.
    var_sm : str
        Variable name for soil moisture.
    var_prcp : str
        Variable name for precipitation.
    lat, lon : int or float
        Lat/lon index or coordinate values.
    length_unit : str, optional
        Precipitation length unit (e.g., 'mm', 'cm', 'in', 'm').
    time_unit : str, optional
        Precipitation time unit (e.g., 's', 'h', 'd', 'week').
    sm_timestep : str, optional
        Soil moisture timestep ('h', 'd', 'week', 'month').

    Returns
    -------
    da : xarray.DataArray
        Soil moisture time series.
    prc : xarray.DataArray
        Precipitation time series [converted if units provided].
    """
    logger.info(f"📥 Loading data from SM file: {sm_file} and PRCP file: {prcp_file}")

    # --- Open datasets ---
    df = xr.open_dataset(sm_file, decode_times=False)
    prcp = xr.open_dataset(prcp_file, decode_times=False)
    logger.debug(f"SM dataset dims: {df.dims}, PRCP dataset dims: {prcp.dims}")

    # --- Build time axis for SM ---
    units = df[var_sm].time.attrs["units"]
    origin = np.datetime64(pd.to_datetime(units.split("since")[1].strip()))
    da = df[var_sm].assign_coords(
        time=origin + df[var_sm]["time"].values.astype("timedelta64[D]")
    )

    # --- Select by coordinate or index ---
    lat_values = df["lat"].values
    lon_values = df["lon"].values
    if (lat_values.min() <= lat <= lat_values.max()) and (lon_values.min() <= lon <= lon_values.max()):
        da_point = da.sel(lat=lat, lon=lon, method="nearest")
        prc_point = prcp[var_prcp].sel(lat=lat, lon=lon, method="nearest")
        logger.info(f"📍 Extracted using coordinates: lat={lat}, lon={lon}")
    else:
        da_point = da.isel(lat=int(lat), lon=int(lon))
        prc_point = prcp[var_prcp].isel(lat=int(lat), lon=int(lon))
        logger.info(f"📍 Extracted using indices: lat_idx={lat}, lon_idx={lon}")

    # --- Align time axis ---
    prc_point["time"] = da_point["time"].values
    logger.debug("Aligned precipitation time axis with soil moisture.")

    # --- Optional unit conversion ---
    if length_unit and time_unit and sm_timestep:
        logger.info(f"🔄 Converting precipitation units: {length_unit}/{time_unit} to {sm_timestep}")
        prc_point = PrecipConverter.convert_precip(
            precip_da=prc_point,
            length_unit=length_unit,
            time_unit=time_unit,
            sm_timestep=sm_timestep
        )
        logger.info("✅ Precipitation converted successfully.")
    else:
        logger.warning("⚠️ Precip unit/timestep not provided — returning raw values.")

    logger.info(f"✅ Data loading completed. Timesteps: {len(da_point['time'])}")
    return da_point, prc_point
