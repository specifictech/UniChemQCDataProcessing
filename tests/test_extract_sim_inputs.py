import os
import tempfile
import pandas as pd
from analytics.extract_sim_inputs import extract_sim_inputs

def test_extract_sim_inputs():
    # Create synthetic data for 2 paired batches, 6 sensors each, both systems
    data = []
    for batch_id, system_name in [("B1", "Stonehenge"), ("B1", "Acropolis"), ("B2", "Stonehenge"), ("B2", "Colosseum")]:
        for sensor in range(1, 7):
            for well in ["D6", "D7", "E6", "E7"]:
                data.append({
                    "batch_id": batch_id,
                    "sensor_id": sensor,
                    "well_id": well,
                    "system_name": system_name,
                    "pct_change": 10.0 + sensor + (0.1 if system_name != "Stonehenge" else 0.0)
                })
    df = pd.DataFrame(data)
    with tempfile.TemporaryDirectory() as tmpdir:
        out_dir = os.path.join(tmpdir, "out")
        result = extract_sim_inputs(df, out_dir=out_dir)
        csv_path = os.path.join(out_dir, "simulation_inputs.csv")
        assert os.path.exists(csv_path)
        df_metrics = pd.read_csv(csv_path)
        assert "mu_L" in df_metrics.columns and "mu_P" in df_metrics.columns and "rho_LP" in df_metrics.columns
        assert "legacy_threshold" in df_metrics.columns
        print("Test passed: extract_sim_inputs")

if __name__ == "__main__":
    test_extract_sim_inputs()
