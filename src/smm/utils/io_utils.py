import os
import json
import pandas as pd

def save_ts_values(Ts_values, output_dir):
    """Save Ts values to CSV and JSON."""
    os.makedirs(output_dir, exist_ok=True)

    # Save as CSV
    df = pd.DataFrame({"Ts": Ts_values})
    csv_path = os.path.join(output_dir, "Ts_values.csv")
    df.to_csv(csv_path, index=False)

    # Save as JSON
    json_path = os.path.join(output_dir, "Ts_values.json")
    with open(json_path, "w") as f:
        json.dump(Ts_values, f)

    return csv_path, json_path

