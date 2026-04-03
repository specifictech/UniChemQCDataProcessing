from typing import Dict

from uniprocessor.src.classes.well import Well
from uniprocessor.src.classes.ink_channel import InkChannel
from uniprocessor.src import constants as const

class Sensor:
    """Represents a single Sensor within a TestRun, containing data for its associated wells.
    
    Attributes:
        sensor_id (str):                      Unique identifier for the sensor.
        run_name (str):                       The run name associated with this sensor.
        frame (int):                          The frame number associated with this sensor.
        run_date (str):                       Date of the run.
        sensor_print_date (str):              Sensor print date.
        analyte (str):                        Analyte information.
        run_num (str):                        Run number.
        img_type (str):                       Image type ('run' or 'incubation').
        data (pd.DataFrame):                  DataFrame containing all data for this sensor.
        wells (Dict[str, Dict[str, Any]]):    Dictionary of Well objects keyed by well ID.
        sensor_regular_performance_val (float):       Regular performance value at the sensor level.
        sensor_regular_performance_res (str):         Regular performance result at the sensor level.
        sensor_leak_performance_val (float):  Leak performance value at the sensor level.
        sensor_leak_performance_res (str):    Leak performance result at the sensor level.
    """
    def __init__(self,
                 sensor_id, 
                 run_name, 
                 frame, 
                 run_date,
                 sensor_print_date,
                 analyte,
                 run_num,
                 img_type,
                 data):
        self.sensor_id = sensor_id
        self.run_name = run_name
        self.frame = frame
        self.run_date = run_date
        self.sensor_print_date = sensor_print_date
        self.analyte = analyte
        self.run_num = run_num
        self.img_type = img_type
        self.data = data
        self.wells = self.create_wells_and_ink_channels()
        
        self._sensor_regular_performance_val = None
        self._sensor_regular_performance_res = None
        self._sensor_leak_performance_val = None
        self._sensor_leak_performance_res = None
        
    def __repr__(self):
        return f"Sensor ID: {self.sensor_id}, Run Name: {self.run_name}, Frame: {self.frame}, Wells: {self.wells}"
   
    @property
    def sensor_regular_performance_val(self):
        return self._sensor_regular_performance_val
    @sensor_regular_performance_val.setter
    def sensor_regular_performance_val(self, value):
        self._sensor_regular_performance_val = value
    
    @property
    def sensor_regular_performance_res(self):
        return self._sensor_regular_performance_res
    @sensor_regular_performance_res.setter
    def sensor_regular_performance_res(self, value):
        self._sensor_regular_performance_res = value
    
    @property
    def sensor_leak_performance_val(self):
        return self._sensor_leak_performance_val
    @sensor_leak_performance_val.setter
    def sensor_leak_performance_val(self, value):
        self._sensor_leak_performance_val = value
    
    @property
    def sensor_leak_performance_res(self):
        return self._sensor_leak_performance_res
    @sensor_leak_performance_res.setter
    def sensor_leak_performance_res(self, value):
        self._sensor_leak_performance_res = value
   
    def create_wells_and_ink_channels(self) -> Dict[str, Well]:
        """Within a single sensor, create unique wells and their corresponding InkChannels, grouping data by 'Well' and 'Spot ID'.

        Returns:
            Dict[str, Well]: Dictionary where key = well ID, value = Well object.
        """
        wells = {}
        row_dicts = self.data.to_dict(orient='records') # Dict of dicts where key = well, value = row (sub-dict)
        
        for row in row_dicts:
            well_id = row[const.PROC_COL_WELL]
            
            if well_id not in wells:
                wells[well_id] = Well(well_id, row[const.PROC_COL_SPOT_TYPE])
            
            # Create InkChannel objects for R and G channels
            ink_channel_id = row[const.PROC_COL_SPOT_ID].rstrip('.0') # e.g., '33.52.0' -> '33.52'
            if row[const.PROC_COL_SPOT_TYPE] == const.PROC_SPOT_TYPE_LEAK_SPOT:
                ink_channel_id += ' LD'                               # Leak detector spot IDs have ' LD' suffix
            
            ink_channel_id_r = ink_channel_id + ' R'                  # Red color channel
            ink_channel_id_g = ink_channel_id + ' G'                  # Green color channel
            
            wells[well_id].ink_channels[ink_channel_id_r] = InkChannel(ink_channel_id_r, 
                                                                       diff_perc_val=row[const.PROC_COL_R_DIFF_PERC], 
                                                                       cor_inc_val=row[const.PROC_COL_R_C])
            wells[well_id].ink_channels[ink_channel_id_g] = InkChannel(ink_channel_id_g, 
                                                                       diff_perc_val=row[const.PROC_COL_G_DIFF_PERC], 
                                                                       cor_inc_val=row[const.PROC_COL_G_C])
            
        return wells