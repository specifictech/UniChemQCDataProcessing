from datetime import datetime
import pandas as pd

import constants as const
from classes.ink_channel import InkChannel

class Lot:
    def __init__(self, lot_num, file_path, analysis_date, operator):
        self.lot_num = lot_num
        self.file_path = file_path
        self.analysis_date = analysis_date
        self.operator = operator
        self.software_version = const.SOFTWARE_VERSION
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.data = self.get_lot_data()
        self.sensor_counts = self.get_sensor_counts()
        
        self.chan_passed = 0
        self.chan_failed = 0
        self.final_lot_disposition = None
        
        self.ink_channels = self.create_ink_channels()
        self.lot_summary = self.create_lot_summary_result()
        #self.lot_summary.to_csv(f"./output/lot_summary_{self.lot_num}.csv", index=False)
    
    def __repr__(self):
        return f"Lot(lot_num={self.lot_num}, file_path={self.file_path}, analysis_date={self.analysis_date}, operator={self.operator})"
    
    def get_lot_data(self):
        data = pd.DataFrame()
    
        try:
            data = pd.read_csv(self.file_path, usecols=const.INPUT_COLS)
            data = data[data[const.INPUT_BATCH_ID] == self.lot_num]
            data = data.groupby(const.INPUT_SENSOR_NUM).agg(self.custom_agg).reset_index()
            #data.to_csv(f"./output/processed_{self.lot_num}.csv", index=False)
            
        except FileNotFoundError:
            print(f"Error: The file for lot {self.lot_num} was not found at path: {self.file_path}")
        except Exception as e:
            print(f"An error occurred while reading the file for lot {self.lot_num}: {e}")
            
        return data
    
    def custom_agg(self, series : pd.Series):
        vals = series.dropna().unique()
        if len(vals) == 0:
            return None
        elif len(vals) == 1:
            return vals[0]
        else:
            return list(vals)
    
    def get_sensor_counts(self):
        sensor_counts = {}
        
        for row_tuple in self.data.itertuples(index=False):
            analyte = row_tuple.sensor_num.split("_")[0]
            if analyte not in sensor_counts:
                sensor_counts[analyte] = 1
            else:
                sensor_counts[analyte] += 1
        
        return sensor_counts
    
    def create_ink_channels(self):
        ink_channels = {}
        
        for ic in const.INK_CHANNELS:
            ic_name = ic.split(" ")
            spot_id = " ".join(ic_name[:-1])
            channel = ic_name[-1]
            
            if spot_id not in ink_channels:
                ink_channels[spot_id] = \
                    [InkChannel(
                        spot_id,
                        channel,
                        self.sensor_counts,
                        self.data
                    )]
            else:
                ink_channels[spot_id].append(
                    InkChannel(
                        spot_id,
                        channel,
                        self.sensor_counts,
                        self.data
                    )
                )
                
            if ink_channels[spot_id][-1].result == "PASS":
                self.chan_passed += 1
            else:
                self.chan_failed += 1
        
        #print(f"Lot {self.lot_num} - Channels Passed: {self.chan_passed}, Channels Failed: {self.chan_failed}")
        
        if self.chan_failed > 0:
            self.final_lot_disposition = const.FAIL
        else:
            self.final_lot_disposition = const.PASS
        
        return ink_channels
    
    def create_lot_summary_result(self):
        lot_summary_res_df = pd.DataFrame(columns=const.LOT_SUMMARY_COLS)
        
        for spot_id in self.ink_channels:
            green_chan_res = self.ink_channels[spot_id][0].result
            red_chan_res = self.ink_channels[spot_id][1].result
            lot_summary_res_df.loc[len(lot_summary_res_df)] = {
                const.LOT_SUMMARY_INK: spot_id,
                const.LOT_SUMMARY_GREEN_CHAN: green_chan_res,
                const.LOT_SUMMARY_RED_CHAN: red_chan_res
            }
        
        return lot_summary_res_df