import numpy as np
import xarray as xr
from smm.dataloader import load_data

def test_dataloader_runs(tmp_path):
    """Dummy test — just checks function runs with fake files."""
    # create fake NetCDF
    fake_ds = xr.Dataset({
        "H2OSOI": (("time","lat","lon"), np.random.rand(5, 1, 1))
    }, coords={"time": [0,1,2,3,4], "lat":[0], "lon":[0]})
    fake_ds["H2OSOI"].time.attrs["units"] = "days since 2000-01-01"
    sm_path = tmp_path / "sm.nc"
    fake_ds.to_netcdf(sm_path)

    fake_ds2 = xr.Dataset({
        "PRECTmms": (("time","lat","lon"), np.random.rand(5, 1, 1))
    }, coords={"time": [0,1,2,3,4], "lat":[0], "lon":[0]})
    pr_path = tmp_path / "pr.nc"
    fake_ds2.to_netcdf(pr_path)

    da, prc = load_data(str(sm_path), str(pr_path), "H2OSOI", "PRECTmms", 0, 0)
    assert da.shape[0] == 5
    assert prc.shape[0] == 5

