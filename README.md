# 🛰️ Soil Moisture Memory (SMM) Toolkit

[![Tests](https://github.com/mfarmani95/SMM-Project/actions/workflows/tests.yml/badge.svg)](https://github.com/mfarmani95/SMM-Project/actions)
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

