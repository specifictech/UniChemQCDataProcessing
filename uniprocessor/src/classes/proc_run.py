from typing import Dict
import pandas as pd
import pprint

from uniprocessor.src import constants as const
from uniprocessor.src.classes.batch import Batch

class ProcRun:
    """Encapsulates the data collected from a single analysis.
    
    Attributes:
        src_folder (str):      Path to the source folder containing input files.
        proc_file (str):       Path to the proc file.
        batches (List[Batch]): List of Batch objects.
    """
    def __init__(self, file_path: str):
        self.proc_file = file_path
        self.batches = self.create_batches()
        
    def create_batches(self) -> Dict[str, Batch]:
        batches = {}
        
        try:
            proc_df = pd.read_csv(self.proc_file,
                                  usecols=const.PROC_USED_COLS.keys(),
                                    dtype=const.PROC_USED_COLS)
            
            self.check_for_1e6_bug(proc_df)
            
            # Remove spot IDs '-1' and '-2'
            proc_df = proc_df[~proc_df[const.PROC_COL_SPOT_ID].isin(const.IGNORE_SPOT_IDS)]
            
            # Group by batch ID to get individual batches
            batches_df = proc_df.groupby([const.PROC_COL_BATCH_ID, const.PROC_COL_BATCH]).agg(list).reset_index()
            for row_tuple in batches_df.itertuples(index=False):
                batch_id           = row_tuple.batch_id
                batch              = row_tuple.batch
                batch_data         = pd.DataFrame(row_tuple).T                       # Transpose to get back to original shape
                batch_data.columns = batches_df.columns                       # Restore original column names
                batch_data.drop(columns=[const.PROC_COL_BATCH_ID, const.PROC_COL_BATCH], inplace=True) # Drop grouping columns
                new_cols           = [col for col in batches_df.columns \
                                        if col not in [const.PROC_COL_BATCH_ID, const.PROC_COL_BATCH]] # Update original_cols to exclude dropped columns
                batch_data         = batch_data.explode(new_cols)                     # Explode lists back into rows
                batches[batch_id]  = Batch(batch_id, batch, batch_data)
            
        except FileNotFoundError:
            print(f"Error: The proc file was not found.")
        except Exception as e:
            print(f"An error occurred: {e}")
        
        return batches
    
    def check_for_1e6_bug(self, df: pd.DataFrame) -> None:
        '''Check for the presence of the -1e6 bug/feature in the proc file, report affected lot-run-frames and terminate execution.'''
        
        # Check the G_diff, R_diff, G_diff_perc, R_diff_perc columns
        rows = df[(df[const.PROC_COL_G_DIFF] == const.KNOWN_ERR_VAL) |
                  (df[const.PROC_COL_R_DIFF] == const.KNOWN_ERR_VAL) |
                  (df[const.PROC_COL_G_DIFF_PERC] == const.KNOWN_ERR_VAL) |
                  (df[const.PROC_COL_R_DIFF_PERC] == const.KNOWN_ERR_VAL)]
        
        if not rows.empty:
            # Group by batch_id, analyte, run_num, frame to get unique occurrences
            rows = rows.groupby([const.PROC_COL_BATCH_ID, const.PROC_COL_ANALYTE, const.PROC_COL_RUN_NUM, const.PROC_COL_FRAME]).agg(list).reset_index()
            file_name = self.proc_file.split("/")[-1]
            
            print(f"\n[error] Detected -1e6 value in file \"{file_name}\":")
            for row_tuple in rows.itertuples():
                index = row_tuple.Index + 1
                batch_id   = row_tuple.batch_id
                analyte    = row_tuple.analyte
                run_num    = row_tuple.run_num
                frame      = row_tuple.frame
                print(f"{index}. Lot: {batch_id}, Analyte: {analyte}, Run #: {run_num}, Frame: {frame}")
                
            exit(1)