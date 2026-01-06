import pandas as pd
from typing import Dict

from classes.sensor import Sensor
import constants as const

class Batch:
    def __init__(self, batch_id: str, batch: str, batch_data: pd.DataFrame):
        self.batch_id = batch_id
        self.batch = batch

        self.sensors = self.create_sensors(batch_data)
        
        self._batch_performance_val = None
        self.batch_performance_res = None
        self._batch_uniformity_val = None
        self.batch_uniformity_res = None
        self.batch_disposition = None
        
    def __repr__(self):
        return f"Batch(batch_id={self.batch_id}, batch={self.batch})"
    
    @property
    def batch_performance_val(self):
        return self._batch_performance_val
    @batch_performance_val.setter
    def batch_performance_val(self, value):
        self._batch_performance_val = value
          
    def create_sensors(self, data: pd.DataFrame) -> Dict[str, Sensor]:
        """Create Sensor objects from the given data.

        Args:
            data (pd.DataFrame): The raw data.
        Returns:
            Dict[str, Sensor]: A dictionary where key = sensor ID, value = Sensor object.
        """
        sensors = {}
        analyte_counts = {}
        
        # Filter out "run" img_type rows, only use "incubation" img_type
        inc_data = data[data[const.PROC_COL_IMG_TYPE] == const.PROC_IMG_TYPE_INCUBATION]
        # Use "run_name" and "frame" columns to create Sensor groupings
        inc_data = inc_data.groupby([const.PROC_COL_RUN_NAME, const.PROC_COL_FRAME]).agg(list).reset_index()
        
        cols_to_exclude = [const.PROC_COL_RUN_NAME, const.PROC_COL_FRAME] # Columns used for grouping, to be dropped from individual sensor data
        original_cols = inc_data.columns.tolist()                             # Store original columns before dropping any

        for row_tuple in inc_data.itertuples(index=False):
            run_name          = row_tuple.run_name
            frame             = row_tuple.frame
            
            # Can safely access first element since all rows in group have same value for these columns
            run_date          = row_tuple.run_date[0]
            sensor_print_date = row_tuple.sensor_print_date[0]
            analyte           = row_tuple.analyte[0]
            run_num           = row_tuple.run_num[0]
            img_type          = row_tuple.img_type[0]
            
            # Create unique sensor IDs
            if analyte not in analyte_counts:
                analyte_counts[analyte] = 1
            else:
                analyte_counts[analyte] += 1

            sensor_id = str(analyte) + "_" + str(analyte_counts[analyte]) # ex. NH_1, SO2_5, etc.
            sensor_data = pd.DataFrame(row_tuple).T                       # Transpose to get back to original shape
            sensor_data.columns = original_cols                           # Restore original column names
            sensor_data.drop(columns=cols_to_exclude, inplace=True)       # Drop grouping columns
            new_cols = [col for col in original_cols \
                        if col not in cols_to_exclude]                    # Update original_cols to exclude dropped columns
            sensor_data = sensor_data.explode(new_cols)                   # Explode lists back into rows
            
            # Save as a new Sensor object
            sensors[sensor_id] = Sensor(sensor_id, 
                                        run_name, 
                                        frame,
                                        run_date,
                                        sensor_print_date,
                                        analyte,
                                        run_num,
                                        img_type,
                                        sensor_data)
            
        return sensors