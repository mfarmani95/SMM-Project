import logging

logger = logging.getLogger(__name__)

class PrecipConverter:
    """
    Utility class for converting precipitation data into
    consistent units (m per SM timestep).
    """

    # Conversion factors to meters
    LENGTH_FACTORS = {
        "m": 1.0,
        "mm": 0.001,
        "cm": 0.01,
        "in": 0.0254
    }

    # Time conversion factors in seconds
    TIME_FACTORS = {
        "s": 1,
        "sec": 1,
        "second": 1,
        "min": 60,
        "h": 3600,
        "hr": 3600,
        "hour": 3600,
        "d": 86400,
        "day": 86400,
        "week": 7 * 86400,
        "month": 30 * 86400  # approximate
    }

    @staticmethod
    def get_seconds_for_timestep(timestep: str) -> int:
        """Convert timestep keyword to seconds."""
        ts = timestep.lower()
        if ts not in PrecipConverter.TIME_FACTORS:
            raise ValueError(f"Unsupported timestep '{timestep}'. Supported: {list(PrecipConverter.TIME_FACTORS.keys())}")
        return PrecipConverter.TIME_FACTORS[ts]

    @staticmethod
    def convert_precip(precip_da, length_unit: str, time_unit: str, sm_timestep: str):
        """
        Convert precipitation to meters per SM timestep.

        Parameters
        ----------
        precip_da : xarray.DataArray
            Original precipitation data.
        length_unit : str
            Length unit of precipitation (e.g. 'mm', 'cm', 'in', 'm').
        time_unit : str
            Original time unit of precipitation (e.g. 's', 'h', 'd').
        sm_timestep : str
            Timestep of soil moisture ('h', 'd', 'week', 'month').

        Returns
        -------
        xarray.DataArray
            Converted precipitation [m per SM timestep].
        """
        logger.info(f"Converting precip from [{length_unit}/{time_unit}] to match SM timestep [{sm_timestep}]")

        # --- Validate and get conversion factors ---
        length_unit = length_unit.lower()
        if length_unit not in PrecipConverter.LENGTH_FACTORS:
            raise ValueError(f"Unsupported length unit '{length_unit}'. Supported: {list(PrecipConverter.LENGTH_FACTORS.keys())}")

        time_unit = time_unit.lower()
        sm_timestep = sm_timestep.lower()

        length_factor = PrecipConverter.LENGTH_FACTORS[length_unit]
        precip_seconds = PrecipConverter.get_seconds_for_timestep(time_unit)
        sm_seconds = PrecipConverter.get_seconds_for_timestep(sm_timestep)

        # --- Check timestep relationship ---
        if sm_seconds < precip_seconds:
            logger.error(
                f"❌ Invalid timestep combination: SM timestep [{sm_timestep}] "
                f"is shorter than precipitation timestep [{time_unit}]."
            )
            raise ValueError(
                f"Soil moisture timestep ({sm_timestep}) must be >= precipitation timestep ({time_unit})"
            )

        # --- Convert ---
        # First convert length
        precip_m = precip_da * length_factor

        # Then scale by time ratio
        scale_factor = precip_seconds / sm_seconds
        precip_converted = precip_m * scale_factor

        logger.info(f"✅ Precip conversion complete. Scale factor={scale_factor:.6f}")
        return precip_converted
