import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime
import threading
import time
from turtle import pd
from typing import List
import pandas as pd

import constants as const

from classes.report_run import ReportRun
from classes.report import Report

class UI:
    def __init__(self, root) -> None:
        # Initialize main parent window
        self.root = root
        self.root.title(const.APP_TITLE)
        root.iconbitmap("./src/assets/biomerieux_logo.ico")
        self.root.geometry(f"{const.WINDOW_WIDTH}x{const.WINDOW_HEIGHT}")
        self.center_window(self.root, const.WINDOW_WIDTH, const.WINDOW_HEIGHT)
        self.root.resizable(False, False)
        self.root.option_add("*TCombobox*Listbox.font", (const.FONT, 18))
        
        # Apply modern theme
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Fix readonly combobox background color
        self.style.map("TCombobox",
                       fieldbackground=[("readonly", "white")],
                       background=[("readonly", "white")])
        
        # Hide notebook tabs for a cleaner look
        self.style.layout("TNotebook.Tab", [])
        
        # Global font settings
        self.large_font = (const.FONT, 14)
        self.button_font = (const.FONT, 18, "bold")
        
        # Style buttons (default system colors)
        self.style.configure("TButton",
                             font=self.button_font,
                             padding=10,
                             background="white")
        self.style.configure("Hover.TButton",
                             font=self.button_font,
                             padding=10,
                             background="white")
        
        # Create fonts for components
        self.title_font = (const.FONT, 24, "bold")
        self.label_font = (const.FONT, 18)
        
        # Create notebook for hidden tabbed interface
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Initialize frames for each step
        self.create_file_search_frame()
        self.create_lot_selection_frame()
        self.create_confirmation_frame()
        self.create_output_frame()   
        
    def center_window(self, window, width, height) -> None:
        # Update the window to get accurate dimensions
        window.update_idletasks()
        
        # Get screen dimensions
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        
        # Calculate x & y coordinates for centering
        x = int((screen_width / 2) - (width / 2))
        y = int((screen_height / 2) - (height / 2))
        
        # Set the window's geometry
        window.geometry(f"{width}x{height}+{x}+{y}")
        
    def create_file_search_frame(self):
        self.frm_file_search = ttk.Frame(self.notebook)
        self.notebook.add(self.frm_file_search)

        # Configure grid to center content
        self.frm_file_search.columnconfigure(0, weight=1)
        self.frm_file_search.columnconfigure(1, weight=1)
        for i in range(6):
            self.frm_file_search.rowconfigure(i, weight=1)
            
        # Title label
        lbl_title = ttk.Label(self.frm_file_search, text=const.APP_TITLE, font=self.title_font)
        lbl_title.grid(row=0, column=0, columnspan=2, pady=(30, 20))
        
        # Frame for entering test dates
        frm_dates = ttk.Frame(self.frm_file_search)
        frm_dates.grid(row=1, column=0, columnspan=2, pady=20)
        
        lbl_date = ttk.Label(frm_dates, text="Enter test date(s) (YYYY-MM-DD): ", font=self.label_font)
        lbl_date.grid(row=0, column=0, padx=20, sticky='ne')
        
        self.txt_dates = scrolledtext.ScrolledText(
            frm_dates,
            width=21,
            height=6,
            font=self.label_font,
            wrap=tk.WORD
        )
        self.txt_dates.grid(row=0, column=1, padx=20, sticky='w')

        # Frame for source folder selection
        frm_src_folder = ttk.Frame(self.frm_file_search)
        frm_src_folder.grid(row=2, column=0, columnspan=2, padx=20)

        lbl_source = ttk.Label(frm_src_folder, text="Source folder: ", font=self.label_font)
        lbl_source.grid(row=0, column=0, padx=20, sticky='e')
        
        self.cb_src = ttk.Combobox(
            frm_src_folder,
            values=[
                'QC ("ImageData")',
                'R&D ("RandD-ImageData")'
            ],
            font=self.label_font,
            state="readonly",
            width=22
        )
        self.cb_src.grid(row=0, column=1, padx=20, sticky='w')
        self.cb_src.current(0)
        
        # Next button
        btn_next = ttk.Button(self.frm_file_search, text="NEXT", command=self.find_lot_options)
        btn_next.grid(row=5, column=0, columnspan=2, pady=(0, 30))
        btn_next.configure(width=20)
        
        # Hover effect for Next button
        btn_next.bind("<Enter>", lambda e: btn_next.configure(style="Hover.TButton"))
        btn_next.bind("<Leave>", lambda e: btn_next.configure(style="TButton"))
           
    def find_lot_options(self):
        self.test_dates = self.txt_dates.get("1.0", tk.END).strip().split('\n')
        
        if not self.test_dates or not self.validate_date_format(self.test_dates):
            messagebox.showerror("Input Error", "Please enter valid, unique dates in YYYY-MM-DD format.")
            return
        
        src_folder = self.cb_src.get()
        if src_folder == 'QC ("ImageData")':
            src_folder = "ImageData"
        else:
            src_folder = "RandD-ImageData"
        
        # Check that each test date folder exists
        invalid_test_dates = []
        for test_date in self.test_dates:
            folder_path = f"../{src_folder}/{test_date}"
            if not os.path.exists(folder_path):
                invalid_test_dates.append(test_date)
        if invalid_test_dates:
            messagebox.showerror("Input Error", f"Folder(s) for date(s) {', '.join(invalid_test_dates)} do not exist in folder {src_folder}.")
            return
        
        # Gather result files from each date folder
        self.lot_options = []
        self.lot_to_results = {}
        for test_date in self.test_dates:
            results_dir = f"../{src_folder}/{test_date}/_results"
            result_files = [result_file for result_file in os.listdir(results_dir) if result_file.endswith("-unichemqc-results.csv")]
            for result_file in result_files:
                try:
                    data = pd.read_csv(f"{results_dir}/{result_file}", usecols=[const.INPUT_BATCH_ID])
                    lots = data[const.INPUT_BATCH_ID].unique().tolist()
                    self.lot_options.extend(lots)
                    for lot in lots:
                        self.lot_to_results[lot] = [f"{results_dir}/{result_file}"]
                        
                except FileNotFoundError:
                    print(f"Error: The file {result_file} was not found at path: {results_dir}/{result_file}")
                except Exception as e:
                    print(f"An error occurred while reading the file {result_file}: {e}")
        
        # Populate lot options listbox before switching frames         
        for lot in self.lot_options:
            self.txt_lot_options.insert(tk.END, lot)
        
        # Switch to second frame
        self.notebook.select(self.frm_lot_selection)
    
    def validate_date_format(self, txt_date: List[str]) -> bool:
        date_strs = [date.strip() for date in txt_date]
        
        if len(date_strs) != len(set(date_strs)):
            return False # Check for duplicates
        try:
            for date_str in date_strs:
                datetime.strptime(date_str, "%Y-%m-%d")
            return True
        except ValueError:
            return False
    
    def create_lot_selection_frame(self):
        self.frm_lot_selection = ttk.Frame(self.notebook)
        self.notebook.add(self.frm_lot_selection)
        
        # Configure grid to center content
        self.frm_lot_selection.columnconfigure(0, weight=1)
        self.frm_lot_selection.columnconfigure(1, weight=1)
        for i in range(6):
            self.frm_lot_selection.rowconfigure(i, weight=1)
            
        # Title label
        lbl_title = ttk.Label(self.frm_lot_selection, text=const.APP_TITLE, font=self.title_font)
        lbl_title.grid(row=0, column=0, columnspan=2, pady=(30, 15))
        
        # Frame for lot options
        frm_lot_options = ttk.Frame(self.frm_lot_selection)
        frm_lot_options.grid(row=1, column=0, columnspan=2)
        
        lbl_lot_options = ttk.Label(frm_lot_options, text="Lot options: ", font=self.label_font)
        lbl_lot_options.grid(row=0, column=0, padx=20, sticky='ne')
        
        self.txt_lot_options = tk.Listbox(
            frm_lot_options,
            width=40,
            height=11,
            font=self.label_font,
            selectmode=tk.MULTIPLE,
            activestyle=tk.NONE,
            exportselection=False
        )
        self.txt_lot_options.grid(row=0, column=1, padx=20, sticky='w')
        
        # Frame for buttons
        frm_buttons = ttk.Frame(self.frm_lot_selection)
        frm_buttons.grid(row=5, column=0, columnspan=2, pady=(0, 30))
        
        # BACK button
        btn_back = ttk.Button(frm_buttons, text="BACK",
                                command=lambda: self.notebook.select(self.frm_file_search))
        btn_back.grid(row=0, column=0, padx=20)
        btn_back.configure(width=20)

        # NEXT button
        btn_next = ttk.Button(frm_buttons, text="NEXT",
                                    command=lambda: self.select_lots())
        btn_next.grid(row=0, column=1, padx=20)
        btn_next.configure(width=20)
        
    def select_lots(self):
        selected_indices = self.txt_lot_options.curselection()
        
        if not selected_indices:
            messagebox.showerror("Selection Error", "Please select at least one lot to proceed.")
            return
        
        selected_lots = [self.txt_lot_options.get(i) for i in selected_indices]
        selected_results = [self.lot_to_results[lot] for lot in selected_lots]
        
        self.txt_selected_files.config(state=tk.NORMAL)
        self.txt_selected_folders.config(state=tk.NORMAL)
        
        for selected_result in selected_results:
            result_file = selected_result[0].split("/")[-1]
            if result_file not in self.txt_selected_files.get(0, tk.END):
                self.txt_selected_files.insert(tk.END, result_file)
        for test_date in self.test_dates:
            if test_date not in self.txt_selected_folders.get(0, tk.END):
                self.txt_selected_folders.insert(tk.END, test_date)
            
        self.txt_selected_files.config(state=tk.DISABLED)
        self.txt_selected_folders.config(state=tk.DISABLED)
            
        self.notebook.select(self.frm_confirmation)

    def create_confirmation_frame(self):
        self.frm_confirmation = ttk.Frame(self.notebook)
        self.notebook.add(self.frm_confirmation)
        
        # Configure grid to center content
        self.frm_confirmation.columnconfigure(0, weight=1)
        self.frm_confirmation.columnconfigure(1, weight=1)
        for i in range(6):
            self.frm_confirmation.rowconfigure(i, weight=1)
            
        # Title label
        lbl_title = ttk.Label(self.frm_confirmation, text=const.APP_TITLE, font=self.title_font)
        lbl_title.grid(row=0, column=0, columnspan=2, pady=(30, 15))
        
        # Frame for selected files
        frm_selected_files = ttk.Frame(self.frm_confirmation)
        frm_selected_files.grid(row=1, column=0, pady=20)
        
        lbl_selected_files = ttk.Label(frm_selected_files, text="Selected files: ", font=self.label_font)
        lbl_selected_files.grid(row=0, column=0, padx=5, sticky='ne')
        
        self.txt_selected_files = tk.Listbox(
            frm_selected_files,
            width=33,
            height=8,
            font=self.label_font,
            disabledforeground="black"
        )
        self.txt_selected_files.grid(row=0, column=1, padx=5, sticky='w')
        self.txt_selected_files.config(state=tk.DISABLED)
        
        # Frame for selected folders
        frm_selected_folders = ttk.Frame(self.frm_confirmation)
        frm_selected_folders.grid(row=1, column=1)
        
        lbl_folders = ttk.Label(frm_selected_folders, text="Folders: ", font=self.label_font)
        lbl_folders.grid(row=0, column=0, padx=5, sticky='ne')
        
        self.txt_selected_folders = tk.Listbox(
            frm_selected_folders,
            width=11,
            height=8,
            font=self.label_font,
            disabledforeground="black"
        )
        self.txt_selected_folders.grid(row=0, column=1, padx=5, sticky='w')
        self.txt_selected_folders.config(state=tk.DISABLED)
        
        # Frame for operator name user input
        frm_operator = ttk.Frame(self.frm_confirmation)
        frm_operator.grid(row=2, column=0, columnspan=2)
        
        lbl_operator = ttk.Label(frm_operator, text="Operator name: ", font=self.label_font)
        lbl_operator.grid(row=0, column=0, padx=5, sticky='e')
        
        self.ent_operator = ttk.Entry(frm_operator, font=self.label_font, width=30)
        self.ent_operator.grid(row=0, column=1, padx=5, sticky='w')
        
        # Frame for buttons
        frm_buttons = ttk.Frame(self.frm_confirmation)
        frm_buttons.grid(row=5, column=0, columnspan=2, pady=(0, 30))
        
        # BACK button
        btn_back = ttk.Button(frm_buttons, text="BACK",
                                command=lambda: self.notebook.select(self.frm_lot_selection))
        btn_back.grid(row=0, column=0, padx=20)
        btn_back.configure(width=20)

        # NEXT button
        btn_next = ttk.Button(frm_buttons, text="NEXT",
                                    command=lambda: self.confirm_with_op_name())
        btn_next.grid(row=0, column=1, padx=20)
        btn_next.configure(width=20)
    
    def confirm_with_op_name(self):
        self.operator_name = self.ent_operator.get().strip()
        
        if not self.operator_name:
            messagebox.showerror("Input Error", "Please enter the operator name to proceed.")
            return
        
        run = ReportRun(self.lot_to_results, self.operator_name)
        
        for lot in run.lots:
            Report(lot)
        
        self.notebook.select(self.frm_output)
    
    def create_output_frame(self):
        self.frm_output = ttk.Frame(self.notebook)
        self.notebook.add(self.frm_output)
        
        # Configure grid to center content
        self.frm_output.columnconfigure(0, weight=2)
        self.frm_output.columnconfigure(1, weight=1)
        for i in range(6):
            self.frm_output.rowconfigure(i, weight=1)
            
        # Title label
        lbl_title = ttk.Label(self.frm_output, text=const.APP_TITLE, font=self.title_font)
        lbl_title.grid(row=0, column=0, columnspan=2, pady=(30, 15))
        
        # Frame for output log, progress bar & info
        frm_output_log = ttk.Frame(self.frm_output)
        frm_output_log.grid(row=1, column=0, rowspan=5, sticky='new')
        
        for i in range(2):
            frm_output_log.columnconfigure(i, weight=1)
        for i in range(3):
            frm_output_log.rowconfigure(i, weight=1)
            
        self.txt_output_log = tk.Text(
            frm_output_log,
            width=52,
            height=14,
            font=self.label_font,
            wrap=tk.WORD
        )
        self.txt_output_log.grid(row=0, column=0, columnspan=2)
        
        self.prg_output = ttk.Progressbar(
            frm_output_log,
            orient=tk.HORIZONTAL,
            length=680,
            mode='determinate'
        )
        self.prg_output.grid(row=1, column=0, columnspan=2, pady=(0, 10))
        
        self.lbl_time_remaining = ttk.Label(frm_output_log, text="Time remaining: 00:00:00", font=(const.FONT, 13))
        self.lbl_time_remaining.grid(row=2, column=0, padx=(15, 0), sticky='w')
        
        self.lbl_completion_percent = ttk.Label(frm_output_log, text="Completion: 0%", font=(const.FONT, 13))
        self.lbl_completion_percent.grid(row=2, column=1, padx=(0, 15), sticky='e')
        
        # Textbox for report to folder mapping
        self.txt_report_mapping = tk.Text(
            self.frm_output,
            width=19,
            height=13,
            font=self.label_font,
            wrap=tk.WORD
        )
        self.txt_report_mapping.grid(row=1, column=1, padx=(0, 20), sticky='nsew')
        self.txt_report_mapping.insert(tk.END, "PDF1 -> 2024-01-01\nPDF2 -> 2024-01-02\n...")
        
        # EXIT button
        btn_exit = ttk.Button(self.frm_output, text="EXIT", command=self.root.quit)
        btn_exit.grid(row=5, column=1, padx=(0, 20), pady=15)
        btn_exit.configure(width=10)