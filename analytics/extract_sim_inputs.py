import argparse
import logging
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import argparse
import logging
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Optional, Dict, Any

def _harmonize_columns(df: pd.DataFrame, colmap: Dict[str, str]) -> pd.DataFrame:
    """Lowercase and map columns for harmonization."""
    df = df.copy()
    df.columns = [c.lower() for c in df.columns]
    for k, v in colmap.items():
        if k.lower() in df.columns:
            df.rename(columns={k.lower(): v}, inplace=True)
    return df
  

def _log_warn(msg: str):
    logging.warning(msg)
    print(f"[WARNING] {msg}", file=sys.stderr)

def _log_info(msg: str):
    logging.info(msg)
    print(f"[INFO] {msg}")

def extract_sim_inputs(
    df: pd.DataFrame,
    out_dir: str = "analytics/out",
    center4_cols: str = "center4_mean",
    pillars_mean_col: str = "sensor_mean_96",
    system_col: str = "system_name",
    batch_col: str = "batch_id",
    sensor_col: str = "sensor_id",
    well_col: str = "well_id",
    value_col: str = "pct_change",
    min_sensors: int = 6,
    legacy_threshold: float = 10.0,
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Main extraction logic. Returns dict of YAML keys.
    """
    import warnings
    os.makedirs(out_dir, exist_ok=True)
    # Harmonize columns
    colmap = {
        batch_col: "batch_id",
        sensor_col: "sensor_id",
        well_col: "well_id",
        system_col: "system_name",
        "System": "system_name",  # Map capitalized column name
        pillars_mean_col: "sensor_mean_96",
        center4_cols: "center4_mean"
    }
    df = _harmonize_columns(df, colmap)

    print("[DEBUG] Columns containing 'diff perc':", [c for c in df.columns if 'diff perc' in c.lower()])
    print("[DEBUG] Columns containing 'sensor mean':", [c for c in df.columns if 'sensor mean' in c.lower()])
    print("[DEBUG] Columns containing 'center 4 mean':", [c for c in df.columns if 'center 4 mean' in c.lower()])


    # Create composite sensor_id for uniqueness
    if "sensor_num" in df.columns and "batch_id" in df.columns:
        df["sensor_id"] = df["batch_id"].astype(str) + "_" + df["sensor_num"].astype(str)
    # System mapping
    df["system_type"] = np.where(
        df["system_name"].str.lower() == "stonehenge", "Legacy",
        np.where(df["system_name"].str.lower().isin(["acropolis", "colosseum"]), "Pillars", None)
    )
    dropped = df["system_type"].isna().sum()
    if dropped:
        _log_warn(f"Dropping {dropped} rows with unknown system_name.")
    df = df[df["system_type"].notna()].copy()

    # --- Targeted melt for ink channel values ---
    value_cols = [c for c in df.columns if c.endswith("Diff Perc Val")]
    sensor_mean_cols = [c for c in df.columns if c.endswith("Diff Perc Sensor Mean")]
    center4_mean_cols = [c for c in df.columns if c.endswith("Diff Perc Center 4 mean")]
    id_cols = [c for c in df.columns if c not in value_cols + sensor_mean_cols + center4_mean_cols]

    print("[DEBUG] value_cols:", value_cols)
    print("[DEBUG] sensor_mean_cols:", sensor_mean_cols)
    print("[DEBUG] center4_mean_cols:", center4_mean_cols)
   
    
    # Melt ink channel values
    df_melted = df.melt(id_vars=id_cols, value_vars=value_cols,
                        var_name="ink_channel", value_name="pct_change")

    # Melt sensor mean values
    df_sensor_mean = df.melt(id_vars=id_cols, value_vars=sensor_mean_cols,
                             var_name="ink_channel_sensor_mean", value_name="sensor_mean")
    # Melt center4 mean values
    df_center4_mean = df.melt(id_vars=id_cols, value_vars=center4_mean_cols,
                              var_name="ink_channel_center4_mean", value_name="center4_mean")

    # Harmonize ink_channel names for sensor_mean and center4_mean
    df_sensor_mean["ink_channel"] = df_sensor_mean["ink_channel_sensor_mean"].str.replace(" Diff Perc Sensor Mean", "", regex=False)
    df_center4_mean["ink_channel"] = df_center4_mean["ink_channel_center4_mean"].str.replace(" Diff Perc Center 4 mean", "", regex=False)

    # Merge melted sensor_mean and center4_mean into main melted df
    df = df_melted.merge(df_sensor_mean[["sensor_mean", "ink_channel", *id_cols]], on=id_cols + ["ink_channel"], how="left")
    df = df.merge(df_center4_mean[["center4_mean", "ink_channel", *id_cols]], on=id_cols + ["ink_channel"], how="left")
    # Per-sensor stats
    # ... (implementation will be filled in next step)
    # Define ink/color channels
    ink_channels = [
        "51.9 G", "51.9 R", "33.39 G", "33.39 R", "51.9 LD G", "51.9 LD R"
    ]
    metric_names = [
        "mu_L", "sigma_L_prod_true", "sigma_lot_true_L", "sigma_sensor_L", "legacy_threshold",
        "mu_P", "sigma_P_prod_true", "sigma_lot_true_P", "sigma_sensor_P", "rho_LP",
    ]
    results = []
    for ink in ink_channels:
        # Filtering by analyte for each ink channel
        if ink.startswith("51.9"):
            df_ink = df[(df["ink_channel"].str.lower() == ink.lower()) & (df["analyte"].str.upper() == "SO2")]
        elif ink.startswith("33.39"):
            df_ink = df[(df["ink_channel"].str.lower() == ink.lower()) & (df["analyte"].str.upper() == "NH3")]
        else:
            df_ink = df[df["ink_channel"].str.lower() == ink.lower()]
        metrics = {"ink_channel": ink}
        # --- Legacy system ---
        df_legacy = df_ink[df_ink["system_type"] == "Legacy"].copy()
        center4_wells = ["D6", "D7", "E6", "E7"]
        df_legacy_c4 = df_legacy[df_legacy["well_id"].str.upper().isin(center4_wells)] if "well_id" in df_legacy.columns else df_legacy
        legacy_sensor_stats = df_legacy_c4.groupby(["batch_id", "sensor_id"])["pct_change"].agg(["mean", "std"]).reset_index()
        sigma_sensor_L = legacy_sensor_stats["std"].mean() if not legacy_sensor_stats.empty else np.nan
        metrics["sigma_sensor_L"] = sigma_sensor_L
        legacy_batch_sensor_means = legacy_sensor_stats.groupby("batch_id")["mean"].apply(list)
        legacy_batch_means = legacy_sensor_stats.groupby("batch_id")["mean"].mean()
        metrics["mu_L"] = legacy_batch_means.mean() if not legacy_batch_means.empty else np.nan
        metrics["sd_obs_L_batchmeans"] = legacy_batch_means.std(ddof=1) if len(legacy_batch_means) > 1 else np.nan
        legacy_batch_sensor_vars = legacy_batch_sensor_means.apply(lambda x: np.var(x, ddof=1) if len(x) > 1 else np.nan)
        var_obs_sensor_mean_L = legacy_batch_sensor_vars.mean() if not legacy_batch_sensor_vars.empty else np.nan
        var_obs_batch_mean_L = metrics["sd_obs_L_batchmeans"] ** 2 if not np.isnan(metrics["sd_obs_L_batchmeans"]) else np.nan
        n_sensors_L = 6
        n_wells_L = 4
        sigma_lot_true_L = np.sqrt(max(var_obs_sensor_mean_L - (sigma_sensor_L ** 2) / n_wells_L, 0)) if not np.isnan(var_obs_sensor_mean_L) and not np.isnan(sigma_sensor_L) else np.nan
        metrics["sigma_lot_true_L"] = sigma_lot_true_L
        sigma_L_prod_true = np.sqrt(max(var_obs_batch_mean_L - (sigma_lot_true_L ** 2) / n_sensors_L - (sigma_sensor_L ** 2) / (n_wells_L * n_sensors_L), 0)) if not np.isnan(var_obs_batch_mean_L) and not np.isnan(sigma_lot_true_L) and not np.isnan(sigma_sensor_L) else np.nan
        metrics["sigma_L_prod_true"] = sigma_L_prod_true
        metrics["mu_L_prod"] = metrics["mu_L"]
        metrics["legacy_threshold"] = legacy_threshold
        metrics["n_batches_legacy"] = len(legacy_batch_means)
        # --- Pillars system ---
        df_pillars = df_ink[df_ink["system_type"] == "Pillars"].copy()
        pillars_sensor_stats = df_pillars.groupby(["batch_id", "sensor_id"])["pct_change"].agg(["mean", "std"]).reset_index()
        sigma_sensor_P = pillars_sensor_stats["std"].mean() if not pillars_sensor_stats.empty else np.nan
        metrics["sigma_sensor_P"] = sigma_sensor_P
        pillars_batch_sensor_means = pillars_sensor_stats.groupby("batch_id")["mean"].apply(list)
        pillars_batch_means = pillars_sensor_stats.groupby("batch_id")["mean"].mean()
        metrics["mu_P"] = pillars_batch_means.mean() if not pillars_batch_means.empty else np.nan
        pillars_batch_sensor_vars = pillars_batch_sensor_means.apply(lambda x: np.var(x, ddof=1) if len(x) > 1 else np.nan)
        var_obs_sensor_mean_P = pillars_batch_sensor_vars.mean() if not pillars_batch_sensor_vars.empty else np.nan
        var_obs_batch_mean_P = pillars_batch_means.std(ddof=1) ** 2 if len(pillars_batch_means) > 1 else np.nan
        n_sensors_P = 6
        n_wells_P = 96
        sigma_lot_true_P = np.sqrt(max(var_obs_sensor_mean_P - (sigma_sensor_P ** 2) / n_wells_P, 0)) if not np.isnan(var_obs_sensor_mean_P) and not np.isnan(sigma_sensor_P) else np.nan
        metrics["sigma_lot_true_P"] = sigma_lot_true_P
        sigma_P_prod_true = np.sqrt(max(var_obs_batch_mean_P - (sigma_lot_true_P ** 2) / n_sensors_P - (sigma_sensor_P ** 2) / (n_wells_P * n_sensors_P), 0)) if not np.isnan(var_obs_batch_mean_P) and not np.isnan(sigma_lot_true_P) and not np.isnan(sigma_sensor_P) else np.nan
        metrics["sigma_P_prod_true"] = sigma_P_prod_true
        metrics["mu_P_prod"] = metrics["mu_P"]
        metrics["n_batches_pillars"] = len(pillars_batch_means)
        # --- Cross-system ---
        paired = pd.merge(legacy_batch_means.reset_index(), pillars_batch_means.reset_index(), on="batch_id", suffixes=("_legacy", "_pillars"))
        metrics["n_batches_paired"] = len(paired)
        metrics["rho_LP"] = paired[["mean_legacy", "mean_pillars"]].corr().iloc[0, 1] if len(paired) > 1 else np.nan
        metrics["generated_at_utc"] = datetime.utcnow().isoformat()
        results.append(metrics)
    df_out = pd.DataFrame(results)
    # If you want to restrict columns, define 'cols' as needed, e.g.:
    # cols = ["ink_channel", ...]  # List of columns to keep
    # df_out = df_out[cols]
    csv_path = os.path.join(out_dir, "simulation_inputs.csv")
    df_out.to_csv(csv_path, index=False)
    _log_info(f"Wrote metrics CSV: {csv_path}")
    return df_out

def main():
    parser = argparse.ArgumentParser(description="Extract simulation input metrics for Monte Carlo simulation.")
    parser.add_argument("--in", dest="infile", required=True, help="Input CSV or Parquet file.")
    parser.add_argument("--out", dest="out_dir", default="analytics/out", help="Output directory.")
    parser.add_argument("--center4-cols", default="center4_mean", help="Center-4 mean column(s) for legacy (comma-separated if multiple).")
    parser.add_argument("--pillars-mean-col", default="sensor_mean_96", help="Pillars mean column for 96-well sensors.")
    parser.add_argument("--system-col", default="system_name", help="System name column.")
    parser.add_argument("--batch-col", default="batch_id", help="Batch (lot) column.")
    parser.add_argument("--sensor-col", default="sensor_id", help="Sensor column.")
    parser.add_argument("--well-col", default="well_id", help="Well column.")
    parser.add_argument("--value-col", default="pct_change", help="Percent change value column.")
    parser.add_argument("--min-sensors", type=int, default=6, help="Minimum sensors per batch.")
    parser.add_argument("--legacy-threshold", type=float, default=10.0, help="Legacy pass threshold.")
    parser.add_argument("--verbose", action="store_true", help="Verbose output.")
    args = parser.parse_args()
    # Read input
    ext = os.path.splitext(args.infile)[1].lower()
    if ext == ".csv":
        df = pd.read_csv(args.infile)
    elif ext in (".parquet", ".pq"):
        df = pd.read_parquet(args.infile)
    else:
        raise ValueError(f"Unsupported input file extension: {ext}")
    extract_sim_inputs(
        df,
        out_dir=args.out_dir,
        center4_cols=args.center4_cols,
        pillars_mean_col=args.pillars_mean_col,
        system_col=args.system_col,
        batch_col=args.batch_col,
        sensor_col=args.sensor_col,
        well_col=args.well_col,
        value_col=args.value_col,
        min_sensors=args.min_sensors,
        legacy_threshold=args.legacy_threshold,
        verbose=args.verbose
    )

if __name__ == "__main__":
    main()
