# 🛰️ Soil Moisture Memory (SMM) Toolkit

[![TestPyPI](https://img.shields.io/badge/TestPyPI-smm--toolkit-blue)](https://test.pypi.org/project/smm-toolkit/)
[![PyPI](https://img.shields.io/pypi/v/smm-toolkit.svg)](https://pypi.org/project/smm-toolkit/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![DOI](https://img.shields.io/badge/DOI-10.5194/hess--29--547--2025-blue)](https://doi.org/10.5194/hess-29-547-2025)

This repository provides a Python package for computing **Soil Moisture Memory (SMM)**, as applied in the paper:

> Farmani, M. A., Behrangi, A., Gupta, A., Tavakoly, A., Geheran, M.,  
> *“Do land models miss key soil hydrological processes controlling soil moisture memory?”*  
> **Hydrology and Earth System Sciences (HESS)**, 29, 547–564, 2025.  
> [https://doi.org/10.5194/hess-29-547-2025](https://doi.org/10.5194/hess-29-547-2025)  
> © Author(s) 2025. This work is distributed under the Creative Commons Attribution 4.0 License.

---

## 🌿 Overview

The **SMM Toolkit** detects and analyzes soil moisture drydowns and computes short-term soil moisture memory timescales (Ts) from time series of soil moisture and precipitation.  

Key features:
- 📈 Automatic **drydown detection**
- 🧪 **Exponential curve fitting** and R² filtering
- 🕒 Short-term **timescale (Ts)** computation for positive increments
- 📊 Plotting and result export
- 🧰 YAML-based configuration for reproducible runs
- ⚡ PyPI installable & CI tested

---


## 🧰 Installation

You can install the package directly from PyPI:

```bash
pip install smm-toolkit
```

Or from TestPyPI for development testing:

```bash
pip install -i https://test.pypi.org/simple/ smm-toolkit
```

---

## 🚀 Quick Start

```python
import logging
from pathlib import Path
from smm.main import SMM
from smm.utils.logger import setup_logger

if __name__ == "__main__":
    setup_logger()
    config_path = Path("/path/to/config.yml")
    logging.info(f"Starting SMM analysis using config: {config_path}")
    SMM(config_path)
```

---

## 🧾 Example YAML Configuration

```yaml
data:
  sm_file: "/path/to/SM.nc"
  prcp_file: "/path/to/precip_2019-01.nc"
  var_sm: "SM_Var_Name"
  var_prcp: "PREC_Var_Name"
  lat: 431          # can be index or actual coordinate
  lon: -111.2       # can be index or actual coordinate

parameters:
  thickness: 0.1
  threshold_factor: 0.12
  min_length: 3
  max_zeros: 0
  max_consecutive_positives: 1
  max_gap_days: 6
  r2_threshold: 0.8
  dim: "time"
  precip_length_unit: mm
  precip_time_unit: s
  sm_timestep: day

output:
  save_dir: "path/to/output"
  plot: true
  save_csv: true
```

---

## 🧪 Development Setup

```bash
git clone https://github.com/mfarmani95/SMM-Toolkit.git
cd SMM-Toolkit
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

For conda users:

```bash
conda env create -f environment.yml
conda activate smm-toolkit
```

---

## 🧰 Useful Makefile Commands

| Command             | Description                                |
|----------------------|---------------------------------------------|
| `make install`       | Install package in editable mode           |
| `make dev`           | Install dev dependencies                   |
| `make test`          | Run test suite with pytest                 |
| `make format`        | Auto-format code with Black                |
| `make lint`          | Run static checks with Ruff                |
| `make build`         | Build distribution package                 |
| `make upload-test`   | Upload to TestPyPI                         |
| `make upload`        | Upload to PyPI                             |

---

## 📜 Citation

If you use this toolkit, please cite:

> Farmani, M. A., Behrangi, A., Gupta, A., Tavakoly, A., Geheran, M. (2025).  
> *Do land models miss key soil hydrological processes controlling soil moisture memory?*  
> **Hydrology and Earth System Sciences**, 29, 547–564.  
> DOI: [10.5194/hess-29-547-2025](https://doi.org/10.5194/hess-29-547-2025)

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).  
© 2025 Mohammad A. Farmani.

---

## 💧 Acknowledgements

Developed as part of hydrologic research at the University of Arizona.  
Inspired by the need for reproducible, transparent, and flexible soil moisture memory analysis tools for land–atmosphere interaction studies.


