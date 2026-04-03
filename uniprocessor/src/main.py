
from uniprocessor.src.classes.proc_run import ProcRun
from uniprocessor.src.classes.analysis import Analysis
from uniprocessor.src.classes.report import Report
import argparse
import fnmatch
import os
import signal
import sys
import time
from pathlib import Path
from typing import Set, List
from concurrent.futures import ThreadPoolExecutor
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


# Ensure analytics is importable
analytics_path = str(Path(__file__).resolve().parent.parent.parent / "analytics")
print(f"[debug] analytics_path: {analytics_path}")
print(f"[debug] sys.path before import: {sys.path}")
if analytics_path not in sys.path:
    sys.path.insert(0, analytics_path)
print(f"[debug] sys.path after insert: {sys.path}")

print("[startup] main.py script started", flush=True)

# ---------- Helpers ----------
def _file_size(path: Path) -> int:
    try:
        return path.stat().st_size
    except Exception:
        return -1

def _wait_until_stable(path: Path, settle: float, timeout: float) -> bool:
    """
    Return True once file size stays unchanged for `settle` seconds,
    else False if `timeout` elapses.
    """
    start = time.monotonic()
    last = _file_size(path)
    if last < 0:
        last = 0
    while time.monotonic() - start < timeout:
        time.sleep(settle)
        now = _file_size(path)
        if now > 0 and now == last:
            return True
        last = now
    return False

def _find_results_parent(path: Path) -> Path:
    """
    Return the nearest ancestor directory whose name is exactly '_results'
    or ends with '_results'. If none is found, fall back to the file's parent.
    """
    for parent in path.parents:
        name = parent.name.lower()
        if name == "_results" or name.endswith("_results"):
            return parent
    return path.parent

def _process_file(file_path: Path, overwrite_results: bool) -> str:
    """
    ProcRun -> Analysis.run_analysis() -> Report.generate_report()
    Returns one of: 'exists_kept', 'overridden', 'created'
    """
    proc_run = ProcRun(str(file_path))
    analysis = Analysis(proc_run)
    analysis.run_analysis()
    report = Report(proc_run, analysis)

    # Determine where to save the report (STRICTLY `_results`)
    result_dir = _find_results_parent(file_path)

    # Generate the report in the located `_results` folder
    status = report.generate_report(
        output_dir=result_dir,
        overwrite=overwrite_results,
        source_proc_path=file_path
    )
    return status

# ---------- Event Handler ----------
class ProcFileHandler(FileSystemEventHandler):
    def __init__(
        self,
        pattern: str,
        settle: float,
        timeout: float,
        processed: Set[Path],
        inflight: Set[Path],
        executor: ThreadPoolExecutor,
        overwrite_results: bool,
    ):
        super().__init__()
        self.pattern = pattern
        self.settle = settle
        self.timeout = timeout
        self.processed = processed
        self.inflight = inflight
        self.executor = executor
        self.overwrite_results = overwrite_results

    def _matches(self, path: Path) -> bool:
        # Match against basename and full path
        return fnmatch.fnmatch(path.name, self.pattern) or fnmatch.fnmatch(str(path), self.pattern)

    def _submit_if_needed(self, path: Path):
        if path in self.processed or path in self.inflight:
            return
        if not self._matches(path):
            return
        self.inflight.add(path)
        print(f"\n[queue] {path}")

        def job(p: Path):
            try:
                if _wait_until_stable(p, settle=self.settle, timeout=self.timeout):
                    print(f"\n[analyze] {p}")
                    status = _process_file(p, overwrite_results=self.overwrite_results)
                    # Print [done] only for overridden or created; suppress when exists_kept
                    if status in ("overridden", "created"):
                        print(f"\n[done] {p}")
                    self.processed.add(p)
                else:
                    print(f"\n[skip] {p} (not stable within timeout)")
            except Exception as ex:
                print(f"\n[error] {p}: {ex}")
            finally:
                self.inflight.discard(p)

        self.executor.submit(job, path)

    def on_created(self, event):
        if not event.is_directory:
            self._submit_if_needed(Path(event.src_path))

    def on_modified(self, event):
        if not event.is_directory:
            self._submit_if_needed(Path(event.src_path))

    def on_moved(self, event):
        if not event.is_directory:
            self._submit_if_needed(Path(event.dest_path))

# ---------- Main ----------
def _default_watch_dirs() -> List[Path]:
    """
    Compute default watch roots:
    ../../ImageData and ../../RandD-ImageData relative to this file (uniprocessor/src/main.py).
    These are siblings of the 'uniprocessor' directory.
    """
    # .../uniprocessor/src
    script_dir = Path(__file__).resolve().parent
    # .../<repo-root> (parent of 'uniprocessor')
    parent_of_uniprocessor = script_dir.parent.parent
    return [
        (parent_of_uniprocessor / "ImageData").resolve(),
        (parent_of_uniprocessor / "RandD-ImageData").resolve(),
    ]

def _initial_scan_and_enqueue(
    roots: List[Path],
    recursive: bool,
    handler: ProcFileHandler,
):
    """
    At startup, enqueue any existing matching files so you don't miss anything.
    """
    for root in roots:
        if not root.exists():
            continue
        iterable = root.rglob(handler.pattern) if recursive else root.glob(handler.pattern)
        for p in iterable:
            if p.is_file():
                handler._submit_if_needed(p)

def process_z_folder(z_folder: str, image_data_folder: str, overwrite_results: bool):
    print(f"[start] process_z_folder called", flush=True)
    z_path = Path(z_folder)
    image_data_path = Path(image_data_folder)
    print(f"[info] Checking Z folder: {z_folder}", flush=True)
    print(f"[info] Checking ImageData folder: {image_data_folder}", flush=True)

    if not z_path.exists():
        print(f"[error] Z folder does not exist: {z_folder}", flush=True)
        return
    if not image_data_path.exists():
        print(f"[error] ImageData folder does not exist: {image_data_folder}", flush=True)
        return
    
    print(f"[debug] Finished checking ImageData folder, proceeding to file search...", flush=True)
    files = [p for p in z_path.rglob("*_proc.csv") if p.is_file() and "summary" not in p.name.lower()]
    print(f"[info] Found {len(files)} files to process in {z_folder}", flush=True)
    sys.stdout.flush()

    if not files:
        print("[info] No files found to process.", flush=True)
        sys.stdout.flush()
        return

    for file_path in files:
        print(f"[process] {file_path}", flush=True)
        sys.stdout.flush()
        try:
            # Get the folder name immediately under UniChemQC_Test_Protocol
            rel = file_path.relative_to(z_path)
            top_folder = rel.parts[0] if len(rel.parts) > 1 else "unknown"
            output_name = f"{top_folder}-unichemqc-results.csv"
            output_path = image_data_path / output_name

            proc_run = ProcRun(str(file_path))
            analysis = Analysis(proc_run)
            analysis.run_analysis()
            report = Report(proc_run, analysis)
            status = report.generate_report(
                output_dir=image_data_path,
                overwrite=overwrite_results,
                source_proc_path=file_path,
                report_name=output_name  # Pass custom name
            )
            print(f"[result] {file_path} -> {output_path} ({status})", flush=True)
        except PermissionError as ex:
            print(f"[permission error] {file_path}: {ex}", flush=True)
        except Exception as ex:
            print(f"[error] {file_path}: {ex}", flush=True)
        sys.stdout.flush()

def main():
    print("[main] Starting main()", flush=True)
    """
    Event-driven watcher using watchdog:
    - Watches ../../ImageData and ../../RandD-ImageData (siblings of 'uniprocessor') recursively
    - Filters files by '*_proc.csv'
    - Debounces until file size is stable
    - Processes files concurrently
    - Exits cleanly on Ctrl+C
    """
    parser = argparse.ArgumentParser(
        description=(
            "Analyze new '*_proc.csv' files under ImageData/ and RandD-ImageData/, "
            "which are siblings of the 'uniprocessor' directory."
        )
    )
    parser.add_argument(
        "--dirs",
        nargs="+",
        help=(
            "Optional override: directories to watch (space-separated). "
            "Default is ../../ImageData and ../../RandD-ImageData relative to this script "
            "(siblings of the 'uniprocessor' directory)."
        ),
    )
    parser.add_argument("--recursive", action="store_true", default=True, help="Watch subdirectories.")
    parser.add_argument("--settle", type=float, default=0.5, help="Seconds between size checks.")
    parser.add_argument("--timeout", type=float, default=60.0, help="Max seconds to wait for stability.")
    parser.add_argument("--workers", type=int, default=os.cpu_count() or 4, help="Concurrent analysis workers.")
    parser.add_argument(
        "--overwrite-results",
        action="store_true",
        default=False,
        help="If set, overwrite existing results files. Default: keep existing files."
    )
    parser.add_argument(
        "--process-z-folder",
        action="store_true",
        default=False,
        help="Process all *_proc.csv files in Z:\\UniChemQC_Test_Protocol (excluding 'summary'), save results to ImageData."
    )

    args = parser.parse_args()

    if args.process_z_folder:
        print("[main] --process-z-folder detected, running batch mode...", flush=True)
        process_z_folder(
            z_folder=r"Z:\UniChemQC_Test_Protocol",
            image_data_folder=r"C:\Users\16015039\OneDrive - bioMerieux\Documents\GitHub\UniChemQCDataProcessing\ImageData",
            overwrite_results=args.overwrite_results,
        )
        print("[main] Batch processing complete.", flush=True)
        return

    # Batch processing mode: process all *_proc.csv files in the specified directories and exit
    watch_roots = [Path(p).resolve() for p in args.dirs] if args.dirs else _default_watch_dirs()

    for root in watch_roots:
        if not root.exists():
            print(f"[warn] watch dir not found: {root}")
            continue
        files = root.rglob("*_proc.csv") if args.recursive else root.glob("*_proc.csv")
        for file_path in files:
            if file_path.is_file():
                print(f"[process] {file_path}", flush=True)
                try:
                    _process_file(file_path, overwrite_results=args.overwrite_results)
                except Exception as ex:
                    print(f"[error] {file_path}: {ex}", flush=True)
    print("[main] Batch processing complete.", flush=True)

if __name__ == "__main__":
    main()

    # --- Analytics integration: run extract_sim_inputs after main report ---
    from analytics import extract_sim_inputs
    import pandas as pd
    try:
        # Find and combine all report CSVs in ImageData
        # Always use the top-level ImageData directory
        output_dir = Path(__file__).resolve().parent.parent.parent / "ImageData"
        print(f"[analytics][debug] Looking for CSVs in: {output_dir}")
        csv_files = list(output_dir.glob("*-unichemqc-results.csv"))
        print(f"[analytics][debug] Found files: {[str(f) for f in csv_files]}")
        if csv_files:
            dfs = [pd.read_csv(str(f)) for f in csv_files]
            combined_df = pd.concat(dfs, ignore_index=True)
            extract_sim_inputs.extract_sim_inputs(combined_df, out_dir=str(output_dir))
            print(f"[analytics] Simulation metrics written for {len(csv_files)} files combined.")
        else:
            print("[analytics] No report CSV found for simulation input extraction.")
    except Exception as ex:
        print(f"[analytics] Error running extract_sim_inputs: {ex}")
