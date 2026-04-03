
# UniChemQC Data Processing

This project is responsible for data ingestion, pass/fail analysis, and generation of tabular results CSV files. It operates passively and automatically as new `*_proc.csv` files are generated in watched directories.

## How It Works

The main script (`uniprocessor/src/main.py`) watches for new or updated `*_proc.csv` files in the default data folders and processes them automatically. Analysis results are saved in a `_results` subfolder relative to each input file.

## Usage

Run the main script from the project root:

```sh
python uniprocessor/src/main.py
```

## How to Run the Project

1. **Activate the Python virtual environment** (if not already activated):
   
   **Create and activate the Python virtual environment** (if not already created):
   
   To create a new virtual environment, run this from your project root:
   ```sh
   python -m venv uniprocessor/.venv
   ```

	On Windows (PowerShell):
	```sh
	.\uniprocessor\.venv\Scripts\Activate.ps1
	```
	Or (Command Prompt):
	```sh
	.\uniprocessor\.venv\Scripts\activate.bat
	```

2. **Install dependencies** (if needed):
	```sh
	pip install -r requirements.txt
	```

3. **Run the main script to process data in a specific folder**:

	```sh
	python uniprocessor/src/main.py --dirs "C:\path\to\your\input-folder"
	```
	- You can specify multiple folders by separating them with spaces:
	  ```sh
	  python uniprocessor/src/main.py --dirs "C:\path\to\input1" "C:\path\to\input2"
	  ```
	- Results will be saved in a `_results` folder next to each input file.

4. **Optional arguments:**
	- `--recursive` : Watch subdirectories (default: True)
	- `--overwrite-results` : Overwrite existing results files
	- `--process-z-folder` : Process all `*_proc.csv` files in `Z:\UniChemQC_Test_Protocol` and save results to the main `ImageData` folder

Example:
```sh
python uniprocessor/src/main.py --dirs "C:\Data\MyInputs" --overwrite-results
```

---

### Key Arguments

- `--dirs <folder1> <folder2> ...`  
	Override the default folders to watch for input files. Provide one or more absolute or relative paths. Example:
	```sh
	python uniprocessor/src/main.py --dirs "C:\path\to\input1" "C:\path\to\input2"
	```
	This only changes where the script looks for input files. Results are still saved in a `_results` folder relative to each input file.

- `--recursive`  
	Watch subdirectories (default: True).

- `--overwrite-results`  
	Overwrite existing results files if present.

- `--process-z-folder`  
	Special mode: process all `*_proc.csv` files in `Z:\UniChemQC_Test_Protocol` and save results to the main `ImageData` folder.

### Where Are Results Saved?

For each processed file, the analysis result is saved in the nearest parent folder named `_results` (or ending with `_results`). If no such folder exists, the result is saved in the same folder as the input file.

## Example

```sh
python uniprocessor/src/main.py --dirs "C:\Data\MyInputs"
```
This will watch `C:\Data\MyInputs` for new `*_proc.csv` files and save results in a `_results` folder next to each input file.

## Configuration

Some parameters are controlled by `unichemqc_config.ini` and `input-files/params.csv`.

---
For more details, see the code in `uniprocessor/src/main.py`.
