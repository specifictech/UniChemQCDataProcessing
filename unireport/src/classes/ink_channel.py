import pandas as pd
from typing import Tuple

import constants as const

class InkChannel:
    def __init__(self, spot_id, channel, sensor_counts, lot_data):
        self.spot_id = spot_id
        self.channel = channel
        self.analyte = const.IC_TO_ANALYTE[spot_id + " " + channel]
        
        self.sensor_counts = sensor_counts
        self.lot_data = lot_data
        
        self.results_summary = self.read_data()
        self.passing_sensors, self.failing_sensors = self.count_sensors()
        
        self.result = self.get_result()
        
    def __repr__(self):
        return f"InkChannel(spot_id={self.spot_id}, channel={self.channel})"
    
    def read_data(self) -> pd.DataFrame:
        results_summary = pd.DataFrame(columns=const.IC_RESULTS_SUMMARY_COLS)

        results_summary.loc[len(results_summary)] = self.create_analyte_row()
        results_summary.loc[len(results_summary)] = self.create_performance_row()
        if "LD" not in self.spot_id:
            results_summary.loc[len(results_summary)] = self.create_uniformity_row()
        #results_summary.to_csv(f"./output/debug_ic_summary_{self.spot_id}_{self.channel}.csv", index=False)
        
        return results_summary
        
    def create_analyte_row(self) -> dict:
        spec_vals = []
        for _, row in self.lot_data.iterrows():
            analyte = row['sensor_num'].split("_")[0]
            if analyte == self.analyte:
                spec_vals.append(row.get(f"{self.spot_id} {self.channel} {const.INPUT_WELL_PERFORM_SPEC}", const.NA))
        spec_val = spec_vals[0] if len(spec_vals) > 0 else const.NA
        
        return {
            const.IC_RESULT_SUM_PARAMETER: self.analyte,
            const.IC_RESULT_SUM_SPEC: spec_val,
            const.IC_RESULT_SUM_VALUE: const.NA,
            const.IC_RESULT_SUM_RESULT: const.NA,
            const.IC_RESULT_SUM_BATCH_SPEC: const.NA,
            const.IC_RESULT_SUM_BATCH_VAL: const.NA,
            const.IC_RESULT_SUM_BATCH_RES: const.NA
        }
        
    def create_performance_row(self) -> dict:
        perform_spec = self.lot_data[f"{const.INPUT_SENSOR_PERFORMANCE} {const.INPUT_SPECIFICATION_VALUE}"][0]
        batch_spec = self.lot_data[f"{const.INPUT_BATCH_PERFORMANCE} {const.INPUT_SPECIFICATION_VALUE}"][0]
        
        values, results = [], []
        batch_val, batch_res = const.NA, const.NA
        for _, row in self.lot_data.iterrows():
            analyte = row['sensor_num'].split("_")[0]
            if analyte == self.analyte:
                values.append(row.get(f"{self.spot_id} {self.channel} {const.INPUT_WELL_PASS_RATE}", const.NA))
                results.append(row.get(f"{self.spot_id} {self.channel} {const.INPUT_SENSOR_PERFORMANCE_RESULT}", const.NA))
                
                batch_val = row.get(f"{self.spot_id} {self.channel} {const.INPUT_SENSOR_PASS_RATE}", const.NA)
                batch_res = row.get(f"{self.spot_id} {self.channel} {const.INPUT_BATCH_PERFORMANCE_RESULT}", const.NA)
        
        return {
            const.IC_RESULT_SUM_PARAMETER: "Performance",
            const.IC_RESULT_SUM_SPEC: f"{perform_spec} of wells pass",
            const.IC_RESULT_SUM_VALUE: "\n".join(map(str, values)),
            const.IC_RESULT_SUM_RESULT: "\n".join(map(str, results)),
            const.IC_RESULT_SUM_BATCH_SPEC: f"{batch_spec} of sensors",
            const.IC_RESULT_SUM_BATCH_VAL: batch_val,
            const.IC_RESULT_SUM_BATCH_RES: batch_res
        }
    
    def create_uniformity_row(self) -> dict:
        uniform_spec = self.lot_data[f"{const.INPUT_SENSOR_UNIFORMITY_CV} {const.INPUT_SPECIFICATION_VALUE}"][0]    
        batch_spec = self.lot_data[f"{const.INPUT_BATCH_UNIFORMITY} {const.INPUT_SPECIFICATION_VALUE}"][0]
        
        values, results = [], []
        batch_val, batch_res = const.NA, const.NA
        
        for _, row in self.lot_data.iterrows():
            analyte = row['sensor_num'].split("_")[0]
            if analyte == self.analyte:
                values.append(row.get(f"{self.spot_id} {self.channel} {const.INPUT_SENSOR_CV}", const.NA))
                results.append(row.get(f"{self.spot_id} {self.channel} {const.INPUT_SENSOR_UNIFORMITY_RESULT}", const.NA))
                
                batch_val = row.get(f"{self.spot_id} {self.channel} {const.INPUT_BATCH_UNIFORMITY_PASS_RATE}", const.NA)
                batch_res = row.get(f"{const.INPUT_BATCH_UNIFORMITY} {const.INPUT_RESULT}", const.NA)
    
        return {
            const.IC_RESULT_SUM_PARAMETER: "Uniformity",
            const.IC_RESULT_SUM_SPEC: f"{uniform_spec} (CV of Gci)",
            const.IC_RESULT_SUM_VALUE: "\n".join(map(str, values)),
            const.IC_RESULT_SUM_RESULT: "\n".join(map(str, results)),
            const.IC_RESULT_SUM_BATCH_SPEC: f"{batch_spec} of sensors",
            const.IC_RESULT_SUM_BATCH_VAL: batch_val,
            const.IC_RESULT_SUM_BATCH_RES: batch_res
        }
        
    def count_sensors(self) -> Tuple[int, int]:
        passing, failing = 0, 0
        
        for i in range(self.sensor_counts[self.analyte]):
            perform_res = self.results_summary.iloc[1][const.IC_RESULT_SUM_RESULT][i]  # Performance row -> performance result
            
            if not "LD" in self.spot_id:
                uniform_res = self.results_summary.iloc[2][const.IC_RESULT_SUM_RESULT][i]  # Uniformity row -> uniformity result
                if perform_res == const.PASS and uniform_res == const.PASS:
                    passing += 1
                else:
                    failing += 1
            else:
                if perform_res == const.PASS:
                    passing += 1
                else:
                    failing += 1
                
            #print(f"InkChannel: {self.spot_id} {self.channel} - Sensor {i+1} - Performance: {perform_res}, Uniformity: {uniform_res}")
            #print(f"Current counts - Passing: {passing}, Failing: {failing}")
        
        return passing, failing
    
    def get_result(self) -> str:
        if self.passing_sensors == self.sensor_counts[self.analyte]:
            return const.PASS
        else:
            return const.FAIL