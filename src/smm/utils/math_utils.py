import numpy as np

def exp_model(t, A, B, C):
    """Exponential decay model A * exp(-B * t) + C."""
    return A * np.exp(-B * t) + C
