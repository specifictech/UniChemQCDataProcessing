from classes.lot import Lot

import constants as const

class ReportRun:
    def __init__(self, lot_to_procs, operator_name):
        self.lot_to_procs = lot_to_procs
        self.operator_name = operator_name
        
        self.lots = self.create_lots()
        
        self.software_version = const.SOFTWARE_VERSION
        
    def create_lots(self):
        lots = []
        
        for lot_num, file_path in self.lot_to_procs.items():
            analysis_date = "-".join(file_path.split("/")[-1].split("-")[:3])
            lot = Lot(lot_num, file_path, analysis_date, self.operator_name)
            lots.append(lot)
            
        return lots