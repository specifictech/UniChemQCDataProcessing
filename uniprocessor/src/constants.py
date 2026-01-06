# Folders to check inside parent MFG folder
PROC_FOLDERS = ["ImageData", "RandD-ImageData"]
RESULTS_FOLDER = "_results"
PROC_FILE_ENDING = "_proc.csv"

# Proc file columns
PROC_COL_RUN_NAME           = "run_name"
PROC_COL_RUN_DATE           = "run_date"
PROC_COL_BATCH_ID           = "batch_id"
PROC_COL_SENSOR_PRINT_DATE  = "sensor_print_date"
PROC_COL_BATCH              = "batch"
PROC_COL_ANALYTE            = "analyte"
PROC_COL_RUN_NUM            = "run_num"
PROC_COL_FRAME              = "frame"
PROC_COL_IMG_TYPE           = "img_type"
PROC_COL_SPOT_TYPE          = "spot_type"
PROC_COL_WELL               = "Well"
PROC_COL_SPOT_ID            = "SpotID"
PROC_COL_G_DIFF             = "G_diff"
PROC_COL_R_DIFF             = "R_diff"
PROC_COL_G_DIFF_PERC        = "G_diff_perc"
PROC_COL_R_DIFF_PERC        = "R_diff_perc"
PROC_COL_G_C                = "Gc"
PROC_COL_R_C                = "Rc"

PROC_USED_COLS = {PROC_COL_RUN_NAME: str,
                  PROC_COL_RUN_DATE: str,
                  PROC_COL_BATCH_ID: str,
                  PROC_COL_SENSOR_PRINT_DATE: str,
                  PROC_COL_BATCH: str,
                  PROC_COL_ANALYTE: str,
                  PROC_COL_RUN_NUM: int,
                  PROC_COL_FRAME: str,
                  PROC_COL_IMG_TYPE: str,
                  PROC_COL_SPOT_TYPE: str,
                  PROC_COL_WELL: str,
                  PROC_COL_G_DIFF: float,
                  PROC_COL_R_DIFF: float,
                  PROC_COL_G_DIFF_PERC: float,
                  PROC_COL_R_DIFF_PERC: float,
                  PROC_COL_G_C: float,
                  PROC_COL_R_C: float,
                  PROC_COL_SPOT_ID: str,
}

# Proc file cell filters
PROC_IMG_TYPE_RUN        = "run"
PROC_IMG_TYPE_INCUBATION = "incubation"
PROC_SPOT_TYPE_WELL_SPOT = "well_spot"
PROC_SPOT_TYPE_LEAK_SPOT = "leak_spot"

# Ink channels that are reported
INK_33_39_G     = "33.39 G"
INK_33_39_R     = "33.39 R"
INK_33_52_G     = "33.52 G"
INK_33_52_R     = "33.52 R"
INK_51_12_G     = "51.12 G"
INK_51_12_R     = "51.12 R"
INK_51_9_G      = "51.9 G"
INK_51_9_R      = "51.9 R"
INK_51_9_LD_G   = "51.9 LD G"
INK_51_9_LD_R   = "51.9 LD R"
INK_70_13_G     = "70.13 G"
INK_70_13_R     = "70.13 R"
INK_91_19_G     = "91.19 G"
INK_91_19_R     = "91.19 R"
INK_91_1_G      = "91.1 G"
INK_91_1_R      = "91.1 R"

# Ignored spot IDs
IGNORE_SPOT_IDS = ['-1', '-2']

# Ignore LD spots in uniformity analysis
LEAK_DETECTOR = "LD"

# Parameters for analysis
PARAM_ANALYTE                 = "Analyte" 

PARAM_WELL_PERFORMANCE        = "Well Performance"
PARAM_SENSOR_PERFORMANCE      = "Sensor Performance"
PARAM_BATCH_PERFORMANCE       = "Batch Performance"

PARAM_SENSOR_UNIFORMITY_CV    = "Sensor Uniformity CV"
PARAM_BATCH_UNIFORMITY        = "Batch Uniformity"

PARAM_LOGICAL_OPERATOR        = "Logical Operator"
PARAM_RESULT_TYPE             = "Result Type"
PARAM_SPECIFICATION_VALUE     = "Specification Value"

PARAM_RES_TYPE_PASS_FAIL      = "pass/fail"
PARAM_RES_TYPE_REF            = "reference"

# Test results
TEST_RESULT_PASS = "PASS"
TEST_RESULT_FAIL = "FAIL"
TEST_RESULT_ERR  = "ERROR"

# Known value of cell feature/bug in proc files
KNOWN_ERR_VAL = -1_000_000

# Report generation:
REPORT_NAME_ENDING = "-unichemqc-results.csv"
REPORT_RESULT = "Result"
REPORT_SENSOR_CV = "Sensor CV"
REPORT_SENSOR_UNIFORMITY = "Sensor Uniformity"
REPORT_BATCH_UNIFORMITY = "Batch Uniformity"
REPORT_PASS_RATE = "Pass Rate"
REPORT_BATCH_DISPOSITION = "Batch Disposition"
REPORT_WELL = "Well"
REPORT_SENSOR = "Sensor"
REPORT_BATCH = "Batch"

# Report columns:
REPORT_COL_DIFF_PERC_VAL = " Diff Perc Val"
REPORT_COL_CORRECTED_VAL = " Corrected Val"
REPORT_COL_WELL_PERFORMANCE_SPEC = " Well Performance Specification"
REPORT_COLS = \
            [PROC_COL_RUN_NAME,
            PROC_COL_RUN_DATE, 
            PROC_COL_BATCH_ID,
            PROC_COL_SENSOR_PRINT_DATE,
            PROC_COL_BATCH,
            PROC_COL_ANALYTE,
            PROC_COL_RUN_NUM,
            PROC_COL_FRAME,
            PROC_COL_IMG_TYPE,
            PROC_COL_SPOT_TYPE,
            "sensor_num",
            PROC_COL_WELL,
            
            INK_33_39_G + REPORT_COL_DIFF_PERC_VAL,
            INK_33_39_R + REPORT_COL_DIFF_PERC_VAL,
            INK_33_52_G + REPORT_COL_DIFF_PERC_VAL,
            INK_33_52_R + REPORT_COL_DIFF_PERC_VAL,
            INK_51_12_G + REPORT_COL_DIFF_PERC_VAL,
            INK_51_12_R + REPORT_COL_DIFF_PERC_VAL,
            INK_70_13_G + REPORT_COL_DIFF_PERC_VAL,
            INK_70_13_R + REPORT_COL_DIFF_PERC_VAL,
            INK_51_9_LD_G + REPORT_COL_DIFF_PERC_VAL,
            INK_51_9_LD_R + REPORT_COL_DIFF_PERC_VAL,
            INK_91_19_G + REPORT_COL_DIFF_PERC_VAL,
            INK_91_19_R + REPORT_COL_DIFF_PERC_VAL,
            INK_91_1_G + REPORT_COL_DIFF_PERC_VAL,
            INK_91_1_R + REPORT_COL_DIFF_PERC_VAL,
            INK_51_9_G + REPORT_COL_DIFF_PERC_VAL,
            INK_51_9_R + REPORT_COL_DIFF_PERC_VAL,
            
            INK_33_39_G + REPORT_COL_WELL_PERFORMANCE_SPEC,
            INK_33_39_R + REPORT_COL_WELL_PERFORMANCE_SPEC,
            INK_33_52_G + REPORT_COL_WELL_PERFORMANCE_SPEC,
            INK_33_52_R + REPORT_COL_WELL_PERFORMANCE_SPEC,
            INK_51_12_G + REPORT_COL_WELL_PERFORMANCE_SPEC,
            INK_51_12_R + REPORT_COL_WELL_PERFORMANCE_SPEC,
            INK_70_13_G + REPORT_COL_WELL_PERFORMANCE_SPEC,
            INK_70_13_R + REPORT_COL_WELL_PERFORMANCE_SPEC,
            INK_51_9_LD_G + REPORT_COL_WELL_PERFORMANCE_SPEC,
            INK_51_9_LD_R + REPORT_COL_WELL_PERFORMANCE_SPEC,
            INK_91_19_G + REPORT_COL_WELL_PERFORMANCE_SPEC,
            INK_91_19_R + REPORT_COL_WELL_PERFORMANCE_SPEC,
            INK_91_1_G + REPORT_COL_WELL_PERFORMANCE_SPEC,
            INK_91_1_R + REPORT_COL_WELL_PERFORMANCE_SPEC,
            INK_51_9_G + REPORT_COL_WELL_PERFORMANCE_SPEC,
            INK_51_9_R + REPORT_COL_WELL_PERFORMANCE_SPEC,
            
            INK_33_39_G + " " + PARAM_WELL_PERFORMANCE + " " + REPORT_RESULT,
            INK_33_39_R + " " + PARAM_WELL_PERFORMANCE + " " + REPORT_RESULT,
            INK_33_52_G + " " + PARAM_WELL_PERFORMANCE + " " + REPORT_RESULT,
            INK_33_52_R + " " + PARAM_WELL_PERFORMANCE + " " + REPORT_RESULT,
            INK_51_12_G + " " + PARAM_WELL_PERFORMANCE + " " + REPORT_RESULT,
            INK_51_12_R + " " + PARAM_WELL_PERFORMANCE + " " + REPORT_RESULT,
            INK_70_13_G + " " + PARAM_WELL_PERFORMANCE + " " + REPORT_RESULT,
            INK_70_13_R + " " + PARAM_WELL_PERFORMANCE + " " + REPORT_RESULT,
            INK_51_9_LD_G + " " + PARAM_WELL_PERFORMANCE + " " + REPORT_RESULT,
            INK_51_9_LD_R + " " + PARAM_WELL_PERFORMANCE + " " + REPORT_RESULT,
            INK_91_19_G + " " + PARAM_WELL_PERFORMANCE + " " + REPORT_RESULT,
            INK_91_19_R + " " + PARAM_WELL_PERFORMANCE + " " + REPORT_RESULT,
            INK_91_1_G + " " + PARAM_WELL_PERFORMANCE + " " + REPORT_RESULT,
            INK_91_1_R + " " + PARAM_WELL_PERFORMANCE + " " + REPORT_RESULT,
            INK_51_9_G + " " + PARAM_WELL_PERFORMANCE + " " + REPORT_RESULT,
            INK_51_9_R + " " + PARAM_WELL_PERFORMANCE + " " + REPORT_RESULT,
            
            INK_33_39_G + " " + REPORT_WELL + " " + REPORT_PASS_RATE,
            INK_33_39_R + " " + REPORT_WELL + " " + REPORT_PASS_RATE,
            INK_33_52_G + " " + REPORT_WELL + " " + REPORT_PASS_RATE,
            INK_33_52_R + " " + REPORT_WELL + " " + REPORT_PASS_RATE,
            INK_51_12_G + " " + REPORT_WELL + " " + REPORT_PASS_RATE,
            INK_51_12_R + " " + REPORT_WELL + " " + REPORT_PASS_RATE,
            INK_70_13_G + " " + REPORT_WELL + " " + REPORT_PASS_RATE,
            INK_70_13_R + " " + REPORT_WELL + " " + REPORT_PASS_RATE,
            INK_51_9_LD_G + " " + REPORT_WELL + " " + REPORT_PASS_RATE,
            INK_51_9_LD_R + " " + REPORT_WELL + " " + REPORT_PASS_RATE,
            INK_91_19_G + " " + REPORT_WELL + " " + REPORT_PASS_RATE,
            INK_91_19_R + " " + REPORT_WELL + " " + REPORT_PASS_RATE,
            INK_91_1_G + " " + REPORT_WELL + " " + REPORT_PASS_RATE,
            INK_91_1_R + " " + REPORT_WELL + " " + REPORT_PASS_RATE,
            INK_51_9_G + " " + REPORT_WELL + " " + REPORT_PASS_RATE,
            INK_51_9_R + " " + REPORT_WELL + " " + REPORT_PASS_RATE,
            
            PARAM_SENSOR_PERFORMANCE + " " + PARAM_LOGICAL_OPERATOR,
            PARAM_SENSOR_PERFORMANCE + " " + PARAM_SPECIFICATION_VALUE,
            INK_33_39_G + " " + PARAM_SENSOR_PERFORMANCE + " " + REPORT_RESULT,
            INK_33_39_R + " " + PARAM_SENSOR_PERFORMANCE + " " + REPORT_RESULT,
            INK_33_52_G + " " + PARAM_SENSOR_PERFORMANCE + " " + REPORT_RESULT,
            INK_33_52_R + " " + PARAM_SENSOR_PERFORMANCE + " " + REPORT_RESULT,
            INK_51_12_G + " " + PARAM_SENSOR_PERFORMANCE + " " + REPORT_RESULT,
            INK_51_12_R + " " + PARAM_SENSOR_PERFORMANCE + " " + REPORT_RESULT,
            INK_70_13_G + " " + PARAM_SENSOR_PERFORMANCE + " " + REPORT_RESULT,
            INK_70_13_R + " " + PARAM_SENSOR_PERFORMANCE + " " + REPORT_RESULT,
            INK_51_9_LD_G + " " + PARAM_SENSOR_PERFORMANCE + " " + REPORT_RESULT,
            INK_51_9_LD_R + " " + PARAM_SENSOR_PERFORMANCE + " " + REPORT_RESULT,
            INK_91_19_G + " " + PARAM_SENSOR_PERFORMANCE + " " + REPORT_RESULT,
            INK_91_19_R + " " + PARAM_SENSOR_PERFORMANCE + " " + REPORT_RESULT,
            INK_91_1_G + " " + PARAM_SENSOR_PERFORMANCE + " " + REPORT_RESULT,
            INK_91_1_R + " " + PARAM_SENSOR_PERFORMANCE + " " + REPORT_RESULT,
            INK_51_9_G + " " + PARAM_SENSOR_PERFORMANCE + " " + REPORT_RESULT,
            INK_51_9_R + " " + PARAM_SENSOR_PERFORMANCE + " " + REPORT_RESULT,
            
            INK_33_39_G + " " + REPORT_SENSOR + " " + REPORT_PASS_RATE,
            INK_33_39_R + " " + REPORT_SENSOR + " " + REPORT_PASS_RATE,
            INK_33_52_G + " " + REPORT_SENSOR + " " + REPORT_PASS_RATE,
            INK_33_52_R + " " + REPORT_SENSOR + " " + REPORT_PASS_RATE,
            INK_51_12_G + " " + REPORT_SENSOR + " " + REPORT_PASS_RATE,
            INK_51_12_R + " " + REPORT_SENSOR + " " + REPORT_PASS_RATE,
            INK_70_13_G + " " + REPORT_SENSOR + " " + REPORT_PASS_RATE,
            INK_70_13_R + " " + REPORT_SENSOR + " " + REPORT_PASS_RATE,
            INK_51_9_LD_G + " " + REPORT_SENSOR + " " + REPORT_PASS_RATE,
            INK_51_9_LD_R + " " + REPORT_SENSOR + " " + REPORT_PASS_RATE,
            INK_91_19_G + " " + REPORT_SENSOR + " " + REPORT_PASS_RATE,
            INK_91_19_R + " " + REPORT_SENSOR + " " + REPORT_PASS_RATE,
            INK_91_1_G + " " + REPORT_SENSOR + " " + REPORT_PASS_RATE,
            INK_91_1_R + " " + REPORT_SENSOR + " " + REPORT_PASS_RATE,
            INK_51_9_G + " " + REPORT_SENSOR + " " + REPORT_PASS_RATE,
            INK_51_9_R + " " + REPORT_SENSOR + " " + REPORT_PASS_RATE,
            
            PARAM_BATCH_PERFORMANCE + " " + PARAM_LOGICAL_OPERATOR,
            PARAM_BATCH_PERFORMANCE + " " + PARAM_SPECIFICATION_VALUE,
            INK_33_39_G + " " + PARAM_BATCH_PERFORMANCE + " " + REPORT_RESULT,
            INK_33_39_R + " " + PARAM_BATCH_PERFORMANCE + " " + REPORT_RESULT,
            INK_33_52_G + " " + PARAM_BATCH_PERFORMANCE + " " + REPORT_RESULT,
            INK_33_52_R + " " + PARAM_BATCH_PERFORMANCE + " " + REPORT_RESULT,
            INK_51_12_G + " " + PARAM_BATCH_PERFORMANCE + " " + REPORT_RESULT,
            INK_51_12_R + " " + PARAM_BATCH_PERFORMANCE + " " + REPORT_RESULT,
            INK_70_13_G + " " + PARAM_BATCH_PERFORMANCE + " " + REPORT_RESULT,
            INK_70_13_R + " " + PARAM_BATCH_PERFORMANCE + " " + REPORT_RESULT,
            INK_51_9_LD_G + " " + PARAM_BATCH_PERFORMANCE + " " + REPORT_RESULT,
            INK_51_9_LD_R + " " + PARAM_BATCH_PERFORMANCE + " " + REPORT_RESULT,
            INK_91_19_G + " " + PARAM_BATCH_PERFORMANCE + " " + REPORT_RESULT,
            INK_91_19_R + " " + PARAM_BATCH_PERFORMANCE + " " + REPORT_RESULT,
            INK_91_1_G + " " + PARAM_BATCH_PERFORMANCE + " " + REPORT_RESULT,
            INK_91_1_R + " " + PARAM_BATCH_PERFORMANCE + " " + REPORT_RESULT,
            INK_51_9_G + " " + PARAM_BATCH_PERFORMANCE + " " + REPORT_RESULT,
            INK_51_9_R + " " + PARAM_BATCH_PERFORMANCE + " " + REPORT_RESULT,
            
            INK_33_39_G + REPORT_COL_CORRECTED_VAL,
            INK_33_39_R + REPORT_COL_CORRECTED_VAL,
            INK_33_52_G + REPORT_COL_CORRECTED_VAL,
            INK_33_52_R + REPORT_COL_CORRECTED_VAL,
            INK_51_12_G + REPORT_COL_CORRECTED_VAL,
            INK_51_12_R + REPORT_COL_CORRECTED_VAL,
            INK_70_13_G + REPORT_COL_CORRECTED_VAL,
            INK_70_13_R + REPORT_COL_CORRECTED_VAL,
            INK_51_9_LD_G + REPORT_COL_CORRECTED_VAL,
            INK_51_9_LD_R + REPORT_COL_CORRECTED_VAL,
            INK_91_19_G + REPORT_COL_CORRECTED_VAL,
            INK_91_19_R + REPORT_COL_CORRECTED_VAL,
            INK_91_1_G + REPORT_COL_CORRECTED_VAL,
            INK_91_1_R + REPORT_COL_CORRECTED_VAL,
            INK_51_9_G + REPORT_COL_CORRECTED_VAL,
            INK_51_9_R + REPORT_COL_CORRECTED_VAL,
            
            INK_33_39_G + " " + REPORT_SENSOR_CV,
            INK_33_39_R + " " + REPORT_SENSOR_CV,
            INK_33_52_G + " " + REPORT_SENSOR_CV,
            INK_33_52_R + " " + REPORT_SENSOR_CV,
            INK_51_12_G + " " + REPORT_SENSOR_CV,
            INK_51_12_R + " " + REPORT_SENSOR_CV,
            INK_70_13_G + " " + REPORT_SENSOR_CV,
            INK_70_13_R + " " + REPORT_SENSOR_CV,
            INK_51_9_LD_G + " " + REPORT_SENSOR_CV,
            INK_51_9_LD_R + " " + REPORT_SENSOR_CV,
            INK_91_19_G + " " + REPORT_SENSOR_CV,
            INK_91_19_R + " " + REPORT_SENSOR_CV,
            INK_91_1_G + " " + REPORT_SENSOR_CV,
            INK_91_1_R + " " + REPORT_SENSOR_CV,
            INK_51_9_G + " " + REPORT_SENSOR_CV,
            INK_51_9_R + " " + REPORT_SENSOR_CV,
            
            PARAM_SENSOR_UNIFORMITY_CV + " " + PARAM_LOGICAL_OPERATOR,
            PARAM_SENSOR_UNIFORMITY_CV + " " + PARAM_SPECIFICATION_VALUE,
            INK_33_39_G + " " + REPORT_SENSOR_UNIFORMITY + " " + REPORT_RESULT,
            INK_33_39_R + " " + REPORT_SENSOR_UNIFORMITY + " " + REPORT_RESULT,
            INK_33_52_G + " " + REPORT_SENSOR_UNIFORMITY + " " + REPORT_RESULT,
            INK_33_52_R + " " + REPORT_SENSOR_UNIFORMITY + " " + REPORT_RESULT,
            INK_51_12_G + " " + REPORT_SENSOR_UNIFORMITY + " " + REPORT_RESULT,
            INK_51_12_R + " " + REPORT_SENSOR_UNIFORMITY + " " + REPORT_RESULT,
            INK_70_13_G + " " + REPORT_SENSOR_UNIFORMITY + " " + REPORT_RESULT,
            INK_70_13_R + " " + REPORT_SENSOR_UNIFORMITY + " " + REPORT_RESULT,
            INK_51_9_LD_G + " " + REPORT_SENSOR_UNIFORMITY + " " + REPORT_RESULT,
            INK_51_9_LD_R + " " + REPORT_SENSOR_UNIFORMITY + " " + REPORT_RESULT,
            INK_91_19_G + " " + REPORT_SENSOR_UNIFORMITY + " " + REPORT_RESULT,
            INK_91_19_R + " " + REPORT_SENSOR_UNIFORMITY + " " + REPORT_RESULT,
            INK_91_1_G + " " + REPORT_SENSOR_UNIFORMITY + " " + REPORT_RESULT,
            INK_91_1_R + " " + REPORT_SENSOR_UNIFORMITY + " " + REPORT_RESULT,
            INK_51_9_G + " " + REPORT_SENSOR_UNIFORMITY + " " + REPORT_RESULT,
            INK_51_9_R + " " + REPORT_SENSOR_UNIFORMITY + " " + REPORT_RESULT,
            
            INK_33_39_G + " " + REPORT_BATCH_UNIFORMITY + " " + REPORT_PASS_RATE,
            INK_33_39_R + " " + REPORT_BATCH_UNIFORMITY + " " + REPORT_PASS_RATE,
            INK_33_52_G + " " + REPORT_BATCH_UNIFORMITY + " " + REPORT_PASS_RATE,
            INK_33_52_R + " " + REPORT_BATCH_UNIFORMITY + " " + REPORT_PASS_RATE,
            INK_51_12_G + " " + REPORT_BATCH_UNIFORMITY + " " + REPORT_PASS_RATE,
            INK_51_12_R + " " + REPORT_BATCH_UNIFORMITY + " " + REPORT_PASS_RATE,
            INK_70_13_G + " " + REPORT_BATCH_UNIFORMITY + " " + REPORT_PASS_RATE,
            INK_70_13_R + " " + REPORT_BATCH_UNIFORMITY + " " + REPORT_PASS_RATE,
            INK_51_9_LD_G + " " + REPORT_BATCH_UNIFORMITY + " " + REPORT_PASS_RATE,
            INK_51_9_LD_R + " " + REPORT_BATCH_UNIFORMITY + " " + REPORT_PASS_RATE,
            INK_91_19_G + " " + REPORT_BATCH_UNIFORMITY + " " + REPORT_PASS_RATE,
            INK_91_19_R + " " + REPORT_BATCH_UNIFORMITY + " " + REPORT_PASS_RATE,
            INK_91_1_G + " " + REPORT_BATCH_UNIFORMITY + " " + REPORT_PASS_RATE,
            INK_91_1_R + " " + REPORT_BATCH_UNIFORMITY + " " + REPORT_PASS_RATE,
            INK_51_9_G + " " + REPORT_BATCH_UNIFORMITY + " " + REPORT_PASS_RATE,
            INK_51_9_R + " " + REPORT_BATCH_UNIFORMITY + " " + REPORT_PASS_RATE,
            
            REPORT_BATCH_UNIFORMITY + " " + PARAM_LOGICAL_OPERATOR,
            REPORT_BATCH_UNIFORMITY + " " + PARAM_SPECIFICATION_VALUE,
            REPORT_BATCH_UNIFORMITY + " " + REPORT_RESULT,
            REPORT_BATCH_DISPOSITION
            ]
