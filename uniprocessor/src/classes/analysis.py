import numpy as np
import pandas as pd

import constants as const

class Analysis:
    """Executes the analysis of a proc file using a param LUT, saving results within a ProcRun object to be output later.
    
    Attributes:
        proc_run (ProcRun):            The ProcRun object containing proc file data and parameters.
        params_file (str):             Path to the params file.
        params (dict):                 Lookup table for parameters from the params file.
        analyte_mappings (dict):       Mappings of analytes to the respective ink channels.
        reference_ink_channels (list): List of reference ink channels.
    """
    def __init__(self, proc_run):
        self.proc_run = proc_run
        self.params_file = '../input-files/params.csv' # ! Hardcoded for now
        
        self.params = {}
        self.analyte_mappings = {}
        self.reference_ink_channels = []
        self.parse_params_file()
        
    def parse_params_file(self) -> None:
        """Create a LUT from the params file, map analytes to ink channels, and identify reference ink channels."""
        param_LUT = {}
        analyte_mappings = {}
        reference_ink_channels = []
        
        params_df = pd.DataFrame()
        try:
            params_df = pd.read_csv(self.params_file)
        except FileNotFoundError:
            print(f"Error: The params file was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")
        
        # Use 'Spot ID and Channel' as the key, matches Ink Channel IDs in Batch object
        param_LUT = params_df.set_index('Spot ID and Channel').to_dict('index')
        
        # Map analytes to ink channels
        for ink_channel, row in param_LUT.items():
            analyte = row[const.PARAM_ANALYTE]
            if analyte not in analyte_mappings:
                analyte_mappings[analyte] = [ink_channel]
            else:
                analyte_mappings[analyte].append(ink_channel)
        
        # Identify reference ink channels
        for ink_channel, row in param_LUT.items():
            if row[const.PARAM_WELL_PERFORMANCE + " " + const.PARAM_RESULT_TYPE] == const.PARAM_RES_TYPE_REF:
                reference_ink_channels.append(ink_channel)
        
        self.params = param_LUT
        self.analyte_mappings = analyte_mappings
        self.reference_ink_channels = reference_ink_channels
        
    def run_analysis(self) -> None:
        """Run the full analysis sequence on the Batch objects."""
        for batch in self.proc_run.batches.values():
            self.compute_performance_metrics(batch)
            self.compute_uniformity_metrics(batch)
            
            #print(f"Batch ID: {batch.batch_id}, Performance Res: {batch.batch_performance_res}, Uniformity Res: {batch.batch_uniformity_res}")
        
            # If both performance and uniformity pass, batch passes; else, fails
            if batch.batch_performance_res == const.TEST_RESULT_PASS and \
                batch.batch_uniformity_res == const.TEST_RESULT_PASS:
                batch.batch_disposition = const.TEST_RESULT_PASS
            else:
                batch.batch_disposition = const.TEST_RESULT_FAIL
                
            #print(f"Batch: {batch.batch_id}, Disposition: {batch.batch_disposition}")

    def compute_performance_metrics(self, batch) -> None:
        """Compute the performance metrics at each level (well, sensor, batch)."""
        self.get_well_performance_results(batch)
        self.get_sensor_performance_results(batch)
        self.get_batch_performance_result(batch)
        
    def get_well_performance_results(self, batch) -> None:
        """Compute well performance results by comparing diff_perc_val to param LUT for each ink channel."""
        for sensor in batch.sensors.values():
            for well in sensor.wells.values():
                for ink_channel_id, ink_channel in well.ink_channels.items():
                    ink_channel.well_performance_res = self.diff_perc_val_lookup(ink_channel_id,
                                                                         sensor.analyte,
                                                                         ink_channel.diff_perc_val)
                
                    #print(f"Sensor {sensor.sensor_id}, Well {well.well_id}, Ink Channel {ink_channel_id}, Diff Perc Val: {ink_channel.diff_perc_val}, Well Performance Result: {ink_channel.well_performance_res}")
    
    def get_sensor_performance_results(self, batch) -> None:
        """Compute sensor performance vals and results based on well performance results."""
        for sensor in batch.sensors.values():
            num_passing_regular_wells   = 0
            num_passing_leak_wells      = 0
            total_regular_wells         = 0
            total_leak_wells            = 0
            
            for well in sensor.wells.values():
                # Get ink channels that are non-reference and are mapped to the sensor's analyte (NH3 -> 33.39, SO2 -> 51.9 & 51.9 LD)
                eligible_ink_channels = []
                
                for ink_channel_id in well.ink_channels.keys():
                    if ink_channel_id not in self.reference_ink_channels and \
                        ink_channel_id in self.analyte_mappings[sensor.analyte]:
                            eligible_ink_channels.append(ink_channel_id)
                
                if eligible_ink_channels:
                    if well.spot_type == const.PROC_SPOT_TYPE_WELL_SPOT:
                        total_regular_wells += 1
                        if all(well.ink_channels[ink_channel_id].well_performance_res == const.TEST_RESULT_PASS 
                            for ink_channel_id in eligible_ink_channels):
                            num_passing_regular_wells += 1
                        
                    else: # well.spot_type == const.PROC_SPOT_TYPE_LEAK_SPOT
                        total_leak_wells += 1
                        if all(well.ink_channels[ink_channel_id].well_performance_res == const.TEST_RESULT_PASS 
                            for ink_channel_id in eligible_ink_channels):
                            num_passing_leak_wells += 1
        
            #print(f"Sensor {sensor.sensor_id}, Frame {sensor.frame}, Passing Regular Wells: {num_passing_regular_wells}, Total Regular Wells: {total_regular_wells}, \
            #      Passing Leak Wells: {num_passing_leak_wells}, Total Leak Wells: {total_leak_wells}")
            
            # Compute regular (and leak if applicable) performance vals and results
            sensor.sensor_regular_performance_val = f"{round((num_passing_regular_wells / total_regular_wells) * 100 if total_regular_wells > 0 else 0.0, 4)}%"
            sensor.sensor_regular_performance_res = self.metric_lookup(const.PARAM_SENSOR_PERFORMANCE, float(sensor.sensor_regular_performance_val.rstrip('%')))
            
            if total_leak_wells > 0:
                sensor.sensor_leak_performance_val = f"{round((num_passing_leak_wells / total_leak_wells) * 100 if total_leak_wells > 0 else 0.0, 4)}%"
                sensor.sensor_leak_performance_res = self.metric_lookup(const.PARAM_SENSOR_PERFORMANCE, float(sensor.sensor_leak_performance_val.rstrip('%')))
            
            #print(f"Sensor: {sensor.sensor_id}, Regular Performance Val: {sensor.sensor_regular_performance_val}, Result: {sensor.sensor_regular_performance_res}, Leak Performance Val: {sensor.sensor_leak_performance_val if total_leak_wells > 0 else 'N/A'}, Leak Result: {sensor.sensor_leak_performance_res if total_leak_wells > 0 else 'N/A'}")
            
    def get_batch_performance_result(self, batch) -> None:
        """Compute batch performance val and result based on sensor performance results."""
        num_passing_sensors = 0
        total_sensors = len(batch.sensors)
        
        for sensor in batch.sensors.values():
            if sensor.sensor_regular_performance_res != const.TEST_RESULT_FAIL and \
                sensor.sensor_leak_performance_res != const.TEST_RESULT_FAIL:
                num_passing_sensors += 1
        
        # Performance value = passing sensors / total sensors
        batch.batch_performance_val = f"{round((num_passing_sensors / total_sensors) * 100 if total_sensors > 0 else 0.0, 4)}%"
        batch.batch_performance_res = self.metric_lookup(const.PARAM_BATCH_PERFORMANCE, float(batch.batch_performance_val.rstrip('%')))
        
        #print(f"Batch Performance Value: {batch.batch_performance_val}, Result: {batch.batch_performance_res}")
        
    def compute_uniformity_metrics(self, batch) -> None:
        """Compute the uniformity metrics at each level (sensor, batch)."""
        self.compute_sensor_uniformity_results(batch)
        self.compute_batch_uniformity_result(batch)
        
    def compute_sensor_uniformity_results(self, batch) -> None:
        """Compute sensor uniformity vals and results based on corrected_incubation_val for each ink channel."""
        for sensor in batch.sensors.values():
            # For each ink channel within a given sensor, gather all corrected incubation vals across wells
            cor_inc_vals = {}
            for well in sensor.wells.values():
                for ink_channel_id, ink_channel in well.ink_channels.items():
                    
                    # Skip ink channels not mapped to the sensor's analyte AND leak detector channels
                    if ink_channel_id not in self.analyte_mappings[sensor.analyte] or const.LEAK_DETECTOR in ink_channel_id:
                        continue
                    
                    if ink_channel_id not in cor_inc_vals:
                        cor_inc_vals[ink_channel_id] = [ink_channel.corrected_incubation_val]
                    else:
                        cor_inc_vals[ink_channel_id].append(ink_channel.corrected_incubation_val)
            
            # Once all corrected incubation vals are gathered, compute CV for each ink channel
            cv_vals = {}
            for ink_channel_id, vals in cor_inc_vals.items():
                mean = np.mean(vals) if len(vals) > 0 else 0.0
                stddev = np.std(vals) if len(vals) > 0 else 0.0
                cv = (stddev / mean) if mean != 0 else 0.0
                cv_vals[ink_channel_id] = cv
                #print(f"Sensor {sensor.sensor_id}, Ink Channel {ink_channel_id}, mean: {mean}, stddev: {stddev}, CV: {cv}")
                
            # Save CV values across ink channels
            for well in sensor.wells.values():
                for ink_channel in well.ink_channels.values():
                    if ink_channel.ink_channel_id in cv_vals:
                        ink_channel.sensor_uniformity_val = f"{round(cv_vals[ink_channel.ink_channel_id] * 100, 4)}%"
                        ink_channel.sensor_uniformity_res = self.metric_lookup(const.PARAM_SENSOR_UNIFORMITY_CV,
                                                                                float(ink_channel.sensor_uniformity_val.rstrip('%')))
                    else:
                        ink_channel.sensor_uniformity_val = None
                        ink_channel.sensor_uniformity_res = None
                        
                    #if ink_channel.sensor_uniformity_val is not None:
                    #    print(f"Sensor: {sensor.sensor_id}, Well: {well.well_id}, Ink Channel: {ink_channel.ink_channel_id}, Sensor Uniformity Val: {ink_channel.sensor_uniformity_val}, Result: {ink_channel.sensor_uniformity_res}")
        
    def compute_batch_uniformity_result(self, batch) -> None:
        """Compute batch uniformity val and result based on sensor uniformity results."""
        # Check each sensor to determine whether all eligible ink channels passed
        passing_sensors = 0
        for sensor in batch.sensors.values():
            all_passing = True
            for well in sensor.wells.values():
                for ink_channel in well.ink_channels.values():
                    # Only consider ink channels that are not reference channels
                    if ink_channel.ink_channel_id not in self.reference_ink_channels and \
                    ink_channel.sensor_uniformity_res == const.TEST_RESULT_FAIL:
                        all_passing = False
            if all_passing:
                passing_sensors += 1
                
        # Uniformity value = passing sensors / total sensors
        total_sensors = len(batch.sensors)
        batch.batch_uniformity_val = f"{round((passing_sensors / total_sensors) * 100 if total_sensors > 0 else 0.0, 4)}%"
        batch.batch_uniformity_res = self.metric_lookup(const.PARAM_BATCH_UNIFORMITY, float(batch.batch_uniformity_val.rstrip('%')))
        
        #print(f"Batch Uniformity Value: {batch.batch_uniformity_val}, Result: {batch.batch_uniformity_res}")
 
    def diff_perc_val_lookup(self, ink_channel_id: str, analyte: str, val: float) -> str:
        """Compares a diff_perc value to a corresponding spec value in the parameter file.

        Args:
            ink_channel_id (str): ID of the ink channel.
            analyte (str): The analyte associated with the ink channel.
            val (float): The diff_perc value to compare.

        Returns:
            str: The test result, either pass or fail.
        """
        result = const.TEST_RESULT_FAIL
        
        row = self.params[ink_channel_id]
        row_analyte = row[const.PARAM_ANALYTE]
        row_spec_val = row[const.PARAM_WELL_PERFORMANCE + " " + const.PARAM_SPECIFICATION_VALUE].rstrip('%')
        row_logical_op = row[const.PARAM_WELL_PERFORMANCE + " " + const.PARAM_LOGICAL_OPERATOR]
        row_result_type = row[const.PARAM_WELL_PERFORMANCE + " " + const.PARAM_RESULT_TYPE]
        
        # If analyte doesn't match or it's a reference channel, return empty result
        if row_analyte != analyte or row_result_type == const.PARAM_RES_TYPE_REF:
            return ''
        
        if row_logical_op == '<':
            if float(val) < float(row_spec_val):
                result = const.TEST_RESULT_PASS
            else:
                result = const.TEST_RESULT_FAIL
        else: # ">"
            if float(val) > float(row_spec_val):
                result = const.TEST_RESULT_PASS
            else:
                result = const.TEST_RESULT_FAIL
        
        # print(f"Ink Channel: {ink_channel_id}, Analyte: {analyte}, Diff Perc Val: {val}, Spec Val: {row_spec_val}, Logical Op: {row_logical_op}, Result: {result}")
        
        return result
    
    def metric_lookup(self, param_name: str, val: float) -> str:
        """Compares a metric to a corresponding consistent spec value in the parameter file.

        Args:
            param_name (str): The parameter name to look up.
            val (float): The rate value to compare.

        Returns:
            str: The test result, either pass or fail.
        """
        result = const.TEST_RESULT_FAIL
        
        # Since all rows share the same spec, grab the first one safely
        row = next(iter(self.params))
        row_spec_val = float(self.params[row][param_name + " " + const.PARAM_SPECIFICATION_VALUE].rstrip('%'))
        row_logical_op = self.params[row][param_name + " " + const.PARAM_LOGICAL_OPERATOR]
        
        if row_logical_op == '<':
            if float(val) < float(row_spec_val):
                result = const.TEST_RESULT_PASS
            else:
                result = const.TEST_RESULT_FAIL
        else: # ">"
            if float(val) > float(row_spec_val):
                result = const.TEST_RESULT_PASS
            else:
                result = const.TEST_RESULT_FAIL
                
        return result