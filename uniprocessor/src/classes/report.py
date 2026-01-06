
from datetime import datetime as dt
import csv
import pandas as pd
from dataclasses import dataclass
from pathlib import Path
from typing import Union
import constants as const

class Report:
    def __init__(self, proc_run, analysis):
        self.proc_run = proc_run
        self.analysis = analysis

    def generate_report(
        self,
        output_dir: Union[Path, str] = ".",
        overwrite: bool = False,
        source_proc_path: Union[Path, str] = None
    ) -> str:
        """
        Generate a tabular report (CSV) from the analysis results, saved to output_dir.
        Returns one of: 'exists_kept', 'overridden', 'created'

        If a results file already exists:
          - overwrite=False: keep existing file, print '[exists]' message, return 'exists_kept'.
          - overwrite=True: replace file, print '[override]' message, return 'overridden'.
        If no existing file:
          - create new, print '[create]' message, return 'created'.
        """
        current_day = dt.now().strftime("%Y-%m-%d")
        report_name = f"{current_day}{const.REPORT_NAME_ENDING}"

        # Ensure target directory exists and build full output path
        out_dir = Path(output_dir).resolve()
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / report_name

        src = Path(source_proc_path).resolve() if source_proc_path else None
        existed_before = out_path.exists()

        # If file exists and we're keeping existing, print and return
        if existed_before and not overwrite:
            print(f"\n[exists] Results file already exists for {src if src else '(unknown proc)'} -> {out_path} (keeping existing)")
            return "exists_kept"

        # Build rows only if we're going to write
        rows = self.create_report_rows()

        # Write/overwrite the file
        with open(out_path, mode='w', newline='') as report_file:
            writer = csv.writer(report_file)
            # Write header
            writer.writerow(const.REPORT_COLS)
            # Write data rows
            for row in rows:
                writer.writerow(vars(row).values())

        # Print outcome message and return status
        if existed_before and overwrite:
            print(f"[override] results file overridden for {src if src else '(unknown proc)'} -> {out_path}")
            return "overridden"
        else:
            print(f"[create] new results file created for {src if src else '(unknown proc)'} -> {out_path}")
            return "created"

    def get_ic_data(self, well, ic, getter) -> Union[str, None]:
        res = None
        if ic in well.ink_channels:
            res = getter(well.ink_channels[ic])
        return res

    def get_sensor_data(self, sensor, ic, getter) -> Union[str, None]:
        res = None
        if ic in self.analysis.analyte_mappings.get(sensor.analyte) and \
           ic not in self.analysis.reference_ink_channels:
            res = getter(sensor)
        return res

    def get_batch_data(self, batch, sensor, ic, getter) -> Union[str, None]:
        res = None
        if ic in self.analysis.analyte_mappings.get(sensor.analyte) and \
           ic not in self.analysis.reference_ink_channels:
            res = getter(batch)
        return res

    def get_spec(self, ic, param) -> str:
        logical_op = self.analysis.params[ic][param + " " + const.PARAM_LOGICAL_OPERATOR]
        spec_val = self.analysis.params[ic][param + " " + const.PARAM_SPECIFICATION_VALUE]
        return logical_op + " " + spec_val

    def create_report_rows(self) -> list:
        """Create a list of ReportRow dataclass instances from the Batch object data."""
        report_rows = []
        for batch in self.proc_run.batches.values():
            for sensor_id, sensor in batch.sensors.items():
                for well_id, well in sensor.wells.items():
                    row = ReportRow(
                        run_name=sensor.run_name,
                        run_date=sensor.run_date,
                        batch_id=batch.batch_id,
                        sensor_print_date=sensor.sensor_print_date,
                        batch=batch.batch,
                        analyte=sensor.analyte,
                        run_num=sensor.run_num,
                        frame=sensor.frame,
                        img_type=sensor.img_type,
                        spot_type=well.spot_type,
                        sensor_id=sensor_id,
                        well_id=well_id,
                        ic_33_39_g_diff_perc=self.get_ic_data(well, const.INK_33_39_G, lambda ic: ic.diff_perc_val),
                        ic_33_39_r_diff_perc=self.get_ic_data(well, const.INK_33_39_R, lambda ic: ic.diff_perc_val),
                        ic_33_52_g_diff_perc=self.get_ic_data(well, const.INK_33_52_G, lambda ic: ic.diff_perc_val),
                        ic_33_52_r_diff_perc=self.get_ic_data(well, const.INK_33_52_R, lambda ic: ic.diff_perc_val),
                        ic_51_12_g_diff_perc=self.get_ic_data(well, const.INK_51_12_G, lambda ic: ic.diff_perc_val),
                        ic_51_12_r_diff_perc=self.get_ic_data(well, const.INK_51_12_R, lambda ic: ic.diff_perc_val),
                        ic_70_13_g_diff_perc=self.get_ic_data(well, const.INK_70_13_G, lambda ic: ic.diff_perc_val),
                        ic_70_13_r_diff_perc=self.get_ic_data(well, const.INK_70_13_R, lambda ic: ic.diff_perc_val),
                        ic_51_9_g_ld_diff_perc=self.get_ic_data(well, const.INK_51_9_LD_G, lambda ic: ic.diff_perc_val),
                        ic_51_9_r_ld_diff_perc=self.get_ic_data(well, const.INK_51_9_LD_R, lambda ic: ic.diff_perc_val),
                        ic_91_19_g_diff_perc=self.get_ic_data(well, const.INK_91_19_G, lambda ic: ic.diff_perc_val),
                        ic_91_19_r_diff_perc=self.get_ic_data(well, const.INK_91_19_R, lambda ic: ic.diff_perc_val),
                        ic_91_1_g_diff_perc=self.get_ic_data(well, const.INK_91_1_G, lambda ic: ic.diff_perc_val),
                        ic_91_1_r_diff_perc=self.get_ic_data(well, const.INK_91_1_R, lambda ic: ic.diff_perc_val),
                        ic_51_9_g_diff_perc=self.get_ic_data(well, const.INK_51_9_G, lambda ic: ic.diff_perc_val),
                        ic_51_9_r_diff_perc=self.get_ic_data(well, const.INK_51_9_R, lambda ic: ic.diff_perc_val),
                        ic_33_39_g_spec=self.get_spec(const.INK_33_39_G, const.PARAM_WELL_PERFORMANCE),
                        ic_33_39_r_spec=self.get_spec(const.INK_33_39_R, const.PARAM_WELL_PERFORMANCE),
                        ic_33_52_g_spec=self.get_spec(const.INK_33_52_G, const.PARAM_WELL_PERFORMANCE),
                        ic_33_52_r_spec=self.get_spec(const.INK_33_52_R, const.PARAM_WELL_PERFORMANCE),
                        ic_51_12_g_spec=self.get_spec(const.INK_51_12_G, const.PARAM_WELL_PERFORMANCE),
                        ic_51_12_r_spec=self.get_spec(const.INK_51_12_R, const.PARAM_WELL_PERFORMANCE),
                        ic_70_13_g_spec=self.get_spec(const.INK_70_13_G, const.PARAM_WELL_PERFORMANCE),
                        ic_70_13_r_spec=self.get_spec(const.INK_70_13_R, const.PARAM_WELL_PERFORMANCE),
                        ic_51_9_g_ld_spec=self.get_spec(const.INK_51_9_LD_G, const.PARAM_WELL_PERFORMANCE),
                        ic_51_9_r_ld_spec=self.get_spec(const.INK_51_9_LD_R, const.PARAM_WELL_PERFORMANCE),
                        ic_91_19_g_spec=self.get_spec(const.INK_91_19_G, const.PARAM_WELL_PERFORMANCE),
                        ic_91_19_r_spec=self.get_spec(const.INK_91_19_R, const.PARAM_WELL_PERFORMANCE),
                        ic_91_1_g_spec=self.get_spec(const.INK_91_1_G, const.PARAM_WELL_PERFORMANCE),
                        ic_91_1_r_spec=self.get_spec(const.INK_91_1_R, const.PARAM_WELL_PERFORMANCE),
                        ic_51_9_g_spec=self.get_spec(const.INK_51_9_G, const.PARAM_WELL_PERFORMANCE),
                        ic_51_9_r_spec=self.get_spec(const.INK_51_9_R, const.PARAM_WELL_PERFORMANCE),
                        ic_33_39_g_well_perform_res=self.get_ic_data(well, const.INK_33_39_G, lambda ic: ic.well_performance_res),
                        ic_33_39_r_well_perform_res=self.get_ic_data(well, const.INK_33_39_R, lambda ic: ic.well_performance_res),
                        ic_33_52_g_well_perform_res=self.get_ic_data(well, const.INK_33_52_G, lambda ic: ic.well_performance_res),
                        ic_33_52_r_well_perform_res=self.get_ic_data(well, const.INK_33_52_R, lambda ic: ic.well_performance_res),
                        ic_51_12_g_well_perform_res=self.get_ic_data(well, const.INK_51_12_G, lambda ic: ic.well_performance_res),
                        ic_51_12_r_well_perform_res=self.get_ic_data(well, const.INK_51_12_R, lambda ic: ic.well_performance_res),
                        ic_70_13_g_well_perform_res=self.get_ic_data(well, const.INK_70_13_G, lambda ic: ic.well_performance_res),
                        ic_70_13_r_well_perform_res=self.get_ic_data(well, const.INK_70_13_R, lambda ic: ic.well_performance_res),
                        ic_51_9_g_ld_well_perform_res=self.get_ic_data(well, const.INK_51_9_LD_G, lambda ic: ic.well_performance_res),
                        ic_51_9_r_ld_well_perform_res=self.get_ic_data(well, const.INK_51_9_LD_R, lambda ic: ic.well_performance_res),
                        ic_91_19_g_well_perform_res=self.get_ic_data(well, const.INK_91_19_G, lambda ic: ic.well_performance_res),
                        ic_91_19_r_well_perform_res=self.get_ic_data(well, const.INK_91_19_R, lambda ic: ic.well_performance_res),
                        ic_91_1_g_well_perform_res=self.get_ic_data(well, const.INK_91_1_G, lambda ic: ic.well_performance_res),
                        ic_91_1_r_well_perform_res=self.get_ic_data(well, const.INK_91_1_R, lambda ic: ic.well_performance_res),
                        ic_51_9_g_well_perform_res=self.get_ic_data(well, const.INK_51_9_G, lambda ic: ic.well_performance_res),
                        ic_51_9_r_well_perform_res=self.get_ic_data(well, const.INK_51_9_R, lambda ic: ic.well_performance_res),
                        ic_33_39_g_sensor_perform_val=self.get_sensor_data(sensor, const.INK_33_39_G, lambda s: s.sensor_regular_performance_val),
                        ic_33_39_r_sensor_perform_val=self.get_sensor_data(sensor, const.INK_33_39_R, lambda s: s.sensor_regular_performance_val),
                        ic_33_52_g_sensor_perform_val=self.get_sensor_data(sensor, const.INK_33_52_G, lambda s: s.sensor_regular_performance_val),
                        ic_33_52_r_sensor_perform_val=self.get_sensor_data(sensor, const.INK_33_52_R, lambda s: s.sensor_regular_performance_val),
                        ic_51_12_g_sensor_perform_val=self.get_sensor_data(sensor, const.INK_51_12_G, lambda s: s.sensor_regular_performance_val),
                        ic_51_12_r_sensor_perform_val=self.get_sensor_data(sensor, const.INK_51_12_R, lambda s: s.sensor_regular_performance_val),
                        ic_70_13_g_sensor_perform_val=self.get_sensor_data(sensor, const.INK_70_13_G, lambda s: s.sensor_regular_performance_val),
                        ic_70_13_r_sensor_perform_val=self.get_sensor_data(sensor, const.INK_70_13_R, lambda s: s.sensor_regular_performance_val),
                        ic_51_9_g_ld_sensor_perform_val=self.get_sensor_data(sensor, const.INK_51_9_LD_G, lambda s: s.sensor_leak_performance_val),
                        ic_51_9_r_ld_sensor_perform_val=self.get_sensor_data(sensor, const.INK_51_9_LD_R, lambda s: s.sensor_leak_performance_val),
                        ic_91_19_g_sensor_perform_val=self.get_sensor_data(sensor, const.INK_91_19_G, lambda s: s.sensor_regular_performance_val),
                        ic_91_19_r_sensor_perform_val=self.get_sensor_data(sensor, const.INK_91_19_R, lambda s: s.sensor_regular_performance_val),
                        ic_91_1_g_sensor_perform_val=self.get_sensor_data(sensor, const.INK_91_1_G, lambda s: s.sensor_regular_performance_val),
                        ic_91_1_r_sensor_perform_val=self.get_sensor_data(sensor, const.INK_91_1_R, lambda s: s.sensor_regular_performance_val),
                        ic_51_9_g_sensor_perform_val=self.get_sensor_data(sensor, const.INK_51_9_G, lambda s: s.sensor_regular_performance_val),
                        ic_51_9_r_sensor_perform_val=self.get_sensor_data(sensor, const.INK_51_9_R, lambda s: s.sensor_regular_performance_val),
                        # Use 33.39 G sensor/batch specs for all channels since they're all the same
                        sensor_perform_logical_op=self.analysis.params[const.INK_33_39_G][const.PARAM_SENSOR_PERFORMANCE + " " + const.PARAM_LOGICAL_OPERATOR],
                        sensor_perform_spec_val=self.analysis.params[const.INK_33_39_G][const.PARAM_SENSOR_PERFORMANCE + " " + const.PARAM_SPECIFICATION_VALUE],
                        ic_33_39_g_sensor_perform_res=self.get_sensor_data(sensor, const.INK_33_39_G, lambda s: s.sensor_regular_performance_res),
                        ic_33_39_r_sensor_perform_res=self.get_sensor_data(sensor, const.INK_33_39_R, lambda s: s.sensor_regular_performance_res),
                        ic_33_52_g_sensor_perform_res=self.get_sensor_data(sensor, const.INK_33_52_G, lambda s: s.sensor_regular_performance_res),
                        ic_33_52_r_sensor_perform_res=self.get_sensor_data(sensor, const.INK_33_52_R, lambda s: s.sensor_regular_performance_res),
                        ic_51_12_g_sensor_perform_res=self.get_sensor_data(sensor, const.INK_51_12_G, lambda s: s.sensor_regular_performance_res),
                        ic_51_12_r_sensor_perform_res=self.get_sensor_data(sensor, const.INK_51_12_R, lambda s: s.sensor_regular_performance_res),
                        ic_70_13_g_sensor_perform_res=self.get_sensor_data(sensor, const.INK_70_13_G, lambda s: s.sensor_regular_performance_res),
                        ic_70_13_r_sensor_perform_res=self.get_sensor_data(sensor, const.INK_70_13_R, lambda s: s.sensor_regular_performance_res),
                        ic_51_9_g_ld_sensor_perform_res=self.get_sensor_data(sensor, const.INK_51_9_LD_G, lambda s: s.sensor_leak_performance_res),
                        ic_51_9_r_ld_sensor_perform_res=self.get_sensor_data(sensor, const.INK_51_9_LD_R, lambda s: s.sensor_leak_performance_res),
                        ic_91_19_g_sensor_perform_res=self.get_sensor_data(sensor, const.INK_91_19_G, lambda s: s.sensor_regular_performance_res),
                        ic_91_19_r_sensor_perform_res=self.get_sensor_data(sensor, const.INK_91_19_R, lambda s: s.sensor_regular_performance_res),
                        ic_91_1_g_sensor_perform_res=self.get_sensor_data(sensor, const.INK_91_1_G, lambda s: s.sensor_regular_performance_res),
                        ic_91_1_r_sensor_perform_res=self.get_sensor_data(sensor, const.INK_91_1_R, lambda s: s.sensor_regular_performance_res),
                        ic_51_9_g_sensor_perform_res=self.get_sensor_data(sensor, const.INK_51_9_G, lambda s: s.sensor_regular_performance_res),
                        ic_51_9_r_sensor_perform_res=self.get_sensor_data(sensor, const.INK_51_9_R, lambda s: s.sensor_regular_performance_res),
                        ic_33_39_g_batch_perform_val=self.get_batch_data(batch, sensor, const.INK_33_39_G, lambda b: b.batch_performance_val),
                        ic_33_39_r_batch_perform_val=self.get_batch_data(batch, sensor, const.INK_33_39_R, lambda b: b.batch_performance_val),
                        ic_33_52_g_batch_perform_val=self.get_batch_data(batch, sensor, const.INK_33_52_G, lambda b: b.batch_performance_val),
                        ic_33_52_r_batch_perform_val=self.get_batch_data(batch, sensor, const.INK_33_52_R, lambda b: b.batch_performance_val),
                        ic_51_12_g_batch_perform_val=self.get_batch_data(batch, sensor, const.INK_51_12_G, lambda b: b.batch_performance_val),
                        ic_51_12_r_batch_perform_val=self.get_batch_data(batch, sensor, const.INK_51_12_R, lambda b: b.batch_performance_val),
                        ic_70_13_g_batch_perform_val=self.get_batch_data(batch, sensor, const.INK_70_13_G, lambda b: b.batch_performance_val),
                        ic_70_13_r_batch_perform_val=self.get_batch_data(batch, sensor, const.INK_70_13_R, lambda b: b.batch_performance_val),
                        ic_51_9_g_ld_batch_perform_val=self.get_batch_data(batch, sensor, const.INK_51_9_LD_G, lambda b: b.batch_performance_val),
                        ic_51_9_r_ld_batch_perform_val=self.get_batch_data(batch, sensor, const.INK_51_9_LD_R, lambda b: b.batch_performance_val),
                        ic_91_19_g_batch_perform_val=self.get_batch_data(batch, sensor, const.INK_91_19_G, lambda b: b.batch_performance_val),
                        ic_91_19_r_batch_perform_val=self.get_batch_data(batch, sensor, const.INK_91_19_R, lambda b: b.batch_performance_val),
                        ic_91_1_g_batch_perform_val=self.get_batch_data(batch, sensor, const.INK_91_1_G, lambda b: b.batch_performance_val),
                        ic_91_1_r_batch_perform_val=self.get_batch_data(batch, sensor, const.INK_91_1_R, lambda b: b.batch_performance_val),
                        ic_51_9_g_batch_perform_val=self.get_batch_data(batch, sensor, const.INK_51_9_G, lambda b: b.batch_performance_val),
                        ic_51_9_r_batch_perform_val=self.get_batch_data(batch, sensor, const.INK_51_9_R, lambda b: b.batch_performance_val),
                        batch_perform_logical_op=self.analysis.params[const.INK_33_39_G][const.PARAM_BATCH_PERFORMANCE + " " + const.PARAM_LOGICAL_OPERATOR],
                        batch_perform_spec_val=self.analysis.params[const.INK_33_39_G][const.PARAM_BATCH_PERFORMANCE + " " + const.PARAM_SPECIFICATION_VALUE],
                        ic_33_39_g_batch_perform_res=self.get_batch_data(batch, sensor, const.INK_33_39_G, lambda b: b.batch_performance_res),
                        ic_33_39_r_batch_perform_res=self.get_batch_data(batch, sensor, const.INK_33_39_R, lambda b: b.batch_performance_res),
                        ic_33_52_g_batch_perform_res=self.get_batch_data(batch, sensor, const.INK_33_52_G, lambda b: b.batch_performance_res),
                        ic_33_52_r_batch_perform_res=self.get_batch_data(batch, sensor, const.INK_33_52_R, lambda b: b.batch_performance_res),
                        ic_51_12_g_batch_perform_res=self.get_batch_data(batch, sensor, const.INK_51_12_G, lambda b: b.batch_performance_res),
                        ic_51_12_r_batch_perform_res=self.get_batch_data(batch, sensor, const.INK_51_12_R, lambda b: b.batch_performance_res),
                        ic_70_13_g_batch_perform_res=self.get_batch_data(batch, sensor, const.INK_70_13_G, lambda b: b.batch_performance_res),
                        ic_70_13_r_batch_perform_res=self.get_batch_data(batch, sensor, const.INK_70_13_R, lambda b: b.batch_performance_res),
                        ic_51_9_g_ld_batch_perform_res=self.get_batch_data(batch, sensor, const.INK_51_9_LD_G, lambda b: b.batch_performance_res),
                        ic_51_9_r_ld_batch_perform_res=self.get_batch_data(batch, sensor, const.INK_51_9_LD_R, lambda b: b.batch_performance_res),
                        ic_91_19_g_batch_perform_res=self.get_batch_data(batch, sensor, const.INK_91_19_G, lambda b: b.batch_performance_res),
                        ic_91_19_r_batch_perform_res=self.get_batch_data(batch, sensor, const.INK_91_19_R, lambda b: b.batch_performance_res),
                        ic_91_1_g_batch_perform_res=self.get_batch_data(batch, sensor, const.INK_91_1_G, lambda b: b.batch_performance_res),
                        ic_91_1_r_batch_perform_res=self.get_batch_data(batch, sensor, const.INK_91_1_R, lambda b: b.batch_performance_res),
                        ic_51_9_g_batch_perform_res=self.get_batch_data(batch, sensor, const.INK_51_9_G, lambda b: b.batch_performance_res),
                        ic_51_9_r_batch_perform_res=self.get_batch_data(batch, sensor, const.INK_51_9_R, lambda b: b.batch_performance_res),
                        ic_33_39_g_corrected=self.get_ic_data(well, const.INK_33_39_G, lambda ic: ic.corrected_incubation_val),
                        ic_33_39_r_corrected=self.get_ic_data(well, const.INK_33_39_R, lambda ic: ic.corrected_incubation_val),
                        ic_33_52_g_corrected=self.get_ic_data(well, const.INK_33_52_G, lambda ic: ic.corrected_incubation_val),
                        ic_33_52_r_corrected=self.get_ic_data(well, const.INK_33_52_R, lambda ic: ic.corrected_incubation_val),
                        ic_51_12_g_corrected=self.get_ic_data(well, const.INK_51_12_G, lambda ic: ic.corrected_incubation_val),
                        ic_51_12_r_corrected=self.get_ic_data(well, const.INK_51_12_R, lambda ic: ic.corrected_incubation_val),
                        ic_70_13_g_corrected=self.get_ic_data(well, const.INK_70_13_G, lambda ic: ic.corrected_incubation_val),
                        ic_70_13_r_corrected=self.get_ic_data(well, const.INK_70_13_R, lambda ic: ic.corrected_incubation_val),
                        ic_51_9_g_ld_corrected=self.get_ic_data(well, const.INK_51_9_LD_G, lambda ic: ic.corrected_incubation_val),
                        ic_51_9_r_ld_corrected=self.get_ic_data(well, const.INK_51_9_LD_R, lambda ic: ic.corrected_incubation_val),
                        ic_91_19_g_corrected=self.get_ic_data(well, const.INK_91_19_G, lambda ic: ic.corrected_incubation_val),
                        ic_91_19_r_corrected=self.get_ic_data(well, const.INK_91_19_R, lambda ic: ic.corrected_incubation_val),
                        ic_91_1_g_corrected=self.get_ic_data(well, const.INK_91_1_G, lambda ic: ic.corrected_incubation_val),
                        ic_91_1_r_corrected=self.get_ic_data(well, const.INK_91_1_R, lambda ic: ic.corrected_incubation_val),
                        ic_51_9_g_corrected=self.get_ic_data(well, const.INK_51_9_G, lambda ic: ic.corrected_incubation_val),
                        ic_51_9_r_corrected=self.get_ic_data(well, const.INK_51_9_R, lambda ic: ic.corrected_incubation_val),
                        ic_33_39_g_sensor_uniform_val=self.get_ic_data(well, const.INK_33_39_G, lambda ic: ic.sensor_uniformity_val),
                        ic_33_39_r_sensor_uniform_val=self.get_ic_data(well, const.INK_33_39_R, lambda ic: ic.sensor_uniformity_val),
                        ic_33_52_g_sensor_uniform_val=self.get_ic_data(well, const.INK_33_52_G, lambda ic: ic.sensor_uniformity_val),
                        ic_33_52_r_sensor_uniform_val=self.get_ic_data(well, const.INK_33_52_R, lambda ic: ic.sensor_uniformity_val),
                        ic_51_12_g_sensor_uniform_val=self.get_ic_data(well, const.INK_51_12_G, lambda ic: ic.sensor_uniformity_val),
                        ic_51_12_r_sensor_uniform_val=self.get_ic_data(well, const.INK_51_12_R, lambda ic: ic.sensor_uniformity_val),
                        ic_70_13_g_sensor_uniform_val=self.get_ic_data(well, const.INK_70_13_G, lambda ic: ic.sensor_uniformity_val),
                        ic_70_13_r_sensor_uniform_val=self.get_ic_data(well, const.INK_70_13_R, lambda ic: ic.sensor_uniformity_val),
                        ic_51_9_g_ld_sensor_uniform_val=self.get_ic_data(well, const.INK_51_9_LD_G, lambda ic: ic.sensor_uniformity_val),
                        ic_51_9_r_ld_sensor_uniform_val=self.get_ic_data(well, const.INK_51_9_LD_R, lambda ic: ic.sensor_uniformity_val),
                        ic_91_19_g_sensor_uniform_val=self.get_ic_data(well, const.INK_91_19_G, lambda ic: ic.sensor_uniformity_val),
                        ic_91_19_r_sensor_uniform_val=self.get_ic_data(well, const.INK_91_19_R, lambda ic: ic.sensor_uniformity_val),
                        ic_91_1_g_sensor_uniform_val=self.get_ic_data(well, const.INK_91_1_G, lambda ic: ic.sensor_uniformity_val),
                        ic_91_1_r_sensor_uniform_val=self.get_ic_data(well, const.INK_91_1_R, lambda ic: ic.sensor_uniformity_val),
                        ic_51_9_g_sensor_uniform_val=self.get_ic_data(well, const.INK_51_9_G, lambda ic: ic.sensor_uniformity_val),
                        ic_51_9_r_sensor_uniform_val=self.get_ic_data(well, const.INK_51_9_R, lambda ic: ic.sensor_uniformity_val),
                        sensor_uniform_logical_op=self.analysis.params[const.INK_33_39_G][const.PARAM_SENSOR_UNIFORMITY_CV + " " + const.PARAM_LOGICAL_OPERATOR],
                        sensor_uniform_spec_val=self.analysis.params[const.INK_33_39_G][const.PARAM_SENSOR_UNIFORMITY_CV + " " + const.PARAM_SPECIFICATION_VALUE],
                        ic_33_39_g_sensor_uniform_res=self.get_ic_data(well, const.INK_33_39_G, lambda ic : ic.sensor_uniformity_res),
                        ic_33_39_r_sensor_uniform_res=self.get_ic_data(well, const.INK_33_39_R, lambda ic : ic.sensor_uniformity_res),
                        ic_33_52_g_sensor_uniform_res=self.get_ic_data(well, const.INK_33_52_G, lambda ic : ic.sensor_uniformity_res),
                        ic_33_52_r_sensor_uniform_res=self.get_ic_data(well, const.INK_33_52_R, lambda ic : ic.sensor_uniformity_res),
                        ic_51_12_g_sensor_uniform_res=self.get_ic_data(well, const.INK_51_12_G, lambda ic : ic.sensor_uniformity_res),
                        ic_51_12_r_sensor_uniform_res=self.get_ic_data(well, const.INK_51_12_R, lambda ic : ic.sensor_uniformity_res),
                        ic_70_13_g_sensor_uniform_res=self.get_ic_data(well, const.INK_70_13_G, lambda ic : ic.sensor_uniformity_res),
                        ic_70_13_r_sensor_uniform_res=self.get_ic_data(well, const.INK_70_13_R, lambda ic : ic.sensor_uniformity_res),
                        ic_51_9_g_ld_sensor_uniform_res=self.get_ic_data(well, const.INK_51_9_LD_G, lambda ic : ic.sensor_uniformity_res),
                        ic_51_9_r_ld_sensor_uniform_res=self.get_ic_data(well, const.INK_51_9_LD_R, lambda ic : ic.sensor_uniformity_res),
                        ic_91_19_g_sensor_uniform_res=self.get_ic_data(well, const.INK_91_19_G, lambda ic : ic.sensor_uniformity_res),
                        ic_91_19_r_sensor_uniform_res=self.get_ic_data(well, const.INK_91_19_R, lambda ic : ic.sensor_uniformity_res),
                        ic_91_1_g_sensor_uniform_res=self.get_ic_data(well, const.INK_91_1_G, lambda ic : ic.sensor_uniformity_res),
                        ic_91_1_r_sensor_uniform_res=self.get_ic_data(well, const.INK_91_1_R, lambda ic : ic.sensor_uniformity_res),
                        ic_51_9_g_sensor_uniform_res=self.get_ic_data(well, const.INK_51_9_G, lambda ic : ic.sensor_uniformity_res),
                        ic_51_9_r_sensor_uniform_res=self.get_ic_data(well, const.INK_51_9_R, lambda ic : ic.sensor_uniformity_res),
                        ic_33_39_g_batch_uniform_val=batch.batch_uniformity_val,
                        ic_33_39_r_batch_uniform_val=batch.batch_uniformity_val,
                        ic_33_52_g_batch_uniform_val=batch.batch_uniformity_val,
                        ic_33_52_r_batch_uniform_val=batch.batch_uniformity_val,
                        ic_51_12_g_batch_uniform_val=batch.batch_uniformity_val,
                        ic_51_12_r_batch_uniform_val=batch.batch_uniformity_val,
                        ic_70_13_g_batch_uniform_val=batch.batch_uniformity_val,
                        ic_70_13_r_batch_uniform_val=batch.batch_uniformity_val,
                        ic_51_9_g_ld_batch_uniform_val=batch.batch_uniformity_val,
                        ic_51_9_r_ld_batch_uniform_val=batch.batch_uniformity_val,
                        ic_91_19_g_batch_uniform_val=batch.batch_uniformity_val,
                        ic_91_19_r_batch_uniform_val=batch.batch_uniformity_val,
                        ic_91_1_g_batch_uniform_val=batch.batch_uniformity_val,
                        ic_91_1_r_batch_uniform_val=batch.batch_uniformity_val,
                        ic_51_9_g_batch_uniform_val=batch.batch_uniformity_val,
                        ic_51_9_r_batch_uniform_val=batch.batch_uniformity_val,
                        batch_uniform_logical_op=self.analysis.params[const.INK_33_39_G][const.PARAM_BATCH_UNIFORMITY + " " + const.PARAM_LOGICAL_OPERATOR],
                        batch_uniform_spec_val=self.analysis.params[const.INK_33_39_G][const.PARAM_BATCH_UNIFORMITY + " " + const.PARAM_SPECIFICATION_VALUE],
                        batch_uniformity_res=batch.batch_uniformity_res,
                        batch_disposition=batch.batch_disposition
                    )
                    report_rows.append(row)
        return report_rows

@dataclass
class ReportRow:
    run_name: str
    run_date: str
    batch_id: str
    sensor_print_date: str
    batch: str
    analyte: str
    run_num: str
    frame: str
    img_type: str
    spot_type: str
    sensor_id: str
    well_id: str
    ic_33_39_g_diff_perc: str
    ic_33_39_r_diff_perc: str
    ic_33_52_g_diff_perc: str
    ic_33_52_r_diff_perc: str
    ic_51_12_g_diff_perc: str
    ic_51_12_r_diff_perc: str
    ic_70_13_g_diff_perc: str
    ic_70_13_r_diff_perc: str
    ic_51_9_g_ld_diff_perc: str
    ic_51_9_r_ld_diff_perc: str
    ic_91_19_g_diff_perc: str
    ic_91_19_r_diff_perc: str
    ic_91_1_g_diff_perc: str
    ic_91_1_r_diff_perc: str
    ic_51_9_g_diff_perc: str
    ic_51_9_r_diff_perc: str
    ic_33_39_g_spec: str
    ic_33_39_r_spec: str
    ic_33_52_g_spec: str
    ic_33_52_r_spec: str
    ic_51_12_g_spec: str
    ic_51_12_r_spec: str
    ic_70_13_g_spec: str
    ic_70_13_r_spec: str
    ic_51_9_g_ld_spec: str
    ic_51_9_r_ld_spec: str
    ic_91_19_g_spec: str
    ic_91_19_r_spec: str
    ic_91_1_g_spec: str
    ic_91_1_r_spec: str
    ic_51_9_g_spec: str
    ic_51_9_r_spec: str
    ic_33_39_g_well_perform_res: str
    ic_33_39_r_well_perform_res: str
    ic_33_52_g_well_perform_res: str
    ic_33_52_r_well_perform_res: str
    ic_51_12_g_well_perform_res: str
    ic_51_12_r_well_perform_res: str
    ic_70_13_g_well_perform_res: str
    ic_70_13_r_well_perform_res: str
    ic_51_9_g_ld_well_perform_res: str
    ic_51_9_r_ld_well_perform_res: str
    ic_91_19_g_well_perform_res: str
    ic_91_19_r_well_perform_res: str
    ic_91_1_g_well_perform_res: str
    ic_91_1_r_well_perform_res: str
    ic_51_9_g_well_perform_res: str
    ic_51_9_r_well_perform_res: str
    ic_33_39_g_sensor_perform_val: str
    ic_33_39_r_sensor_perform_val: str
    ic_33_52_g_sensor_perform_val: str
    ic_33_52_r_sensor_perform_val: str
    ic_51_12_g_sensor_perform_val: str
    ic_51_12_r_sensor_perform_val: str
    ic_70_13_g_sensor_perform_val: str
    ic_70_13_r_sensor_perform_val: str
    ic_51_9_g_ld_sensor_perform_val: str
    ic_51_9_r_ld_sensor_perform_val: str
    ic_91_19_g_sensor_perform_val: str
    ic_91_19_r_sensor_perform_val: str
    ic_91_1_g_sensor_perform_val: str
    ic_91_1_r_sensor_perform_val: str
    ic_51_9_g_sensor_perform_val: str
    ic_51_9_r_sensor_perform_val: str
    sensor_perform_logical_op: str
    sensor_perform_spec_val: str
    ic_33_39_g_sensor_perform_res: str
    ic_33_39_r_sensor_perform_res: str
    ic_33_52_g_sensor_perform_res: str
    ic_33_52_r_sensor_perform_res: str
    ic_51_12_g_sensor_perform_res: str
    ic_51_12_r_sensor_perform_res: str
    ic_70_13_g_sensor_perform_res: str
    ic_70_13_r_sensor_perform_res: str
    ic_51_9_g_ld_sensor_perform_res: str
    ic_51_9_r_ld_sensor_perform_res: str
    ic_91_19_g_sensor_perform_res: str
    ic_91_19_r_sensor_perform_res: str
    ic_91_1_g_sensor_perform_res: str
    ic_91_1_r_sensor_perform_res: str
    ic_51_9_g_sensor_perform_res: str
    ic_51_9_r_sensor_perform_res: str
    ic_33_39_g_batch_perform_val: str
    ic_33_39_r_batch_perform_val: str
    ic_33_52_g_batch_perform_val: str
    ic_33_52_r_batch_perform_val: str
    ic_51_12_g_batch_perform_val: str
    ic_51_12_r_batch_perform_val: str
    ic_70_13_g_batch_perform_val: str
    ic_70_13_r_batch_perform_val: str
    ic_51_9_g_ld_batch_perform_val: str
    ic_51_9_r_ld_batch_perform_val: str
    ic_91_19_g_batch_perform_val: str
    ic_91_19_r_batch_perform_val: str
    ic_91_1_g_batch_perform_val: str
    ic_91_1_r_batch_perform_val: str
    ic_51_9_g_batch_perform_val: str
    ic_51_9_r_batch_perform_val: str
    batch_perform_logical_op: str
    batch_perform_spec_val: str
    ic_33_39_g_batch_perform_res: str
    ic_33_39_r_batch_perform_res: str
    ic_33_52_g_batch_perform_res: str
    ic_33_52_r_batch_perform_res: str
    ic_51_12_g_batch_perform_res: str
    ic_51_12_r_batch_perform_res: str
    ic_70_13_g_batch_perform_res: str
    ic_70_13_r_batch_perform_res: str
    ic_51_9_g_ld_batch_perform_res: str
    ic_51_9_r_ld_batch_perform_res: str
    ic_91_19_g_batch_perform_res: str
    ic_91_19_r_batch_perform_res: str
    ic_91_1_g_batch_perform_res: str
    ic_91_1_r_batch_perform_res: str
    ic_51_9_g_batch_perform_res: str
    ic_51_9_r_batch_perform_res: str
    ic_33_39_g_corrected: str
    ic_33_39_r_corrected: str
    ic_33_52_g_corrected: str
    ic_33_52_r_corrected: str
    ic_51_12_g_corrected: str
    ic_51_12_r_corrected: str
    ic_70_13_g_corrected: str
    ic_70_13_r_corrected: str
    ic_51_9_g_ld_corrected: str
    ic_51_9_r_ld_corrected: str
    ic_91_19_g_corrected: str
    ic_91_19_r_corrected: str
    ic_91_1_g_corrected: str
    ic_91_1_r_corrected: str
    ic_51_9_g_corrected: str
    ic_51_9_r_corrected: str
    ic_33_39_g_sensor_uniform_val: str
    ic_33_39_r_sensor_uniform_val: str
    ic_33_52_g_sensor_uniform_val: str
    ic_33_52_r_sensor_uniform_val: str
    ic_51_12_g_sensor_uniform_val: str
    ic_51_12_r_sensor_uniform_val: str
    ic_70_13_g_sensor_uniform_val: str
    ic_70_13_r_sensor_uniform_val: str
    ic_51_9_g_ld_sensor_uniform_val: str
    ic_51_9_r_ld_sensor_uniform_val: str
    ic_91_19_g_sensor_uniform_val: str
    ic_91_19_r_sensor_uniform_val: str
    ic_91_1_g_sensor_uniform_val: str
    ic_91_1_r_sensor_uniform_val: str
    ic_51_9_g_sensor_uniform_val: str
    ic_51_9_r_sensor_uniform_val: str
    sensor_uniform_logical_op: str
    sensor_uniform_spec_val: str
    ic_33_39_g_sensor_uniform_res: str
    ic_33_39_r_sensor_uniform_res: str
    ic_33_52_g_sensor_uniform_res: str
    ic_33_52_r_sensor_uniform_res: str
    ic_51_12_g_sensor_uniform_res: str
    ic_51_12_r_sensor_uniform_res: str
    ic_70_13_g_sensor_uniform_res: str
    ic_70_13_r_sensor_uniform_res: str
    ic_51_9_g_ld_sensor_uniform_res: str
    ic_51_9_r_ld_sensor_uniform_res: str
    ic_91_19_g_sensor_uniform_res: str
    ic_91_19_r_sensor_uniform_res: str
    ic_91_1_g_sensor_uniform_res: str
    ic_91_1_r_sensor_uniform_res: str
    ic_51_9_g_sensor_uniform_res: str
    ic_51_9_r_sensor_uniform_res: str
    ic_33_39_g_batch_uniform_val: str
    ic_33_39_r_batch_uniform_val: str
    ic_33_52_g_batch_uniform_val: str
    ic_33_52_r_batch_uniform_val: str
    ic_51_12_g_batch_uniform_val: str
    ic_51_12_r_batch_uniform_val: str
    ic_70_13_g_batch_uniform_val: str
    ic_70_13_r_batch_uniform_val: str
    ic_51_9_g_ld_batch_uniform_val: str
    ic_51_9_r_ld_batch_uniform_val: str
    ic_91_19_g_batch_uniform_val: str
    ic_91_19_r_batch_uniform_val: str
    ic_91_1_g_batch_uniform_val: str
    ic_91_1_r_batch_uniform_val: str
    ic_51_9_g_batch_uniform_val: str
    ic_51_9_r_batch_uniform_val: str
    batch_uniform_logical_op: str
    batch_uniform_spec_val: str
    batch_uniformity_res: str
    batch_disposition: str
