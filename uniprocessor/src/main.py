
from classes.proc_run import ProcRun
from classes.analysis import Analysis
from classes.report import Report
import argparse
import fnmatch
import os
import signal
import time
from pathlib import Path
from typing import Set, List
from concurrent.futures import ThreadPoolExecutor
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

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

def main():
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

    args = parser.parse_args()

    # Resolve watch roots
    watch_roots = [Path(p).resolve() for p in args.dirs] if args.dirs else _default_watch_dirs()

    # Validate presence (continue if one is missing)
    for root in watch_roots:
        if not root.exists():
            print(f"\n[warn] watch dir not found: {root}")

    processed: Set[Path] = set()
    inflight: Set[Path] = set()
    pattern = "*_proc.csv"

    print(
        f"\n[watch] roots={', '.join(str(r) for r in watch_roots)} "
        f"pattern={pattern} recursive={args.recursive} workers={args.workers} overwrite_results={args.overwrite_results}"
    )

    executor = ThreadPoolExecutor(max_workers=args.workers)
    handler = ProcFileHandler(
        pattern=pattern,
        settle=args.settle,
        timeout=args.timeout,
        processed=processed,
        inflight=inflight,
        executor=executor,
        overwrite_results=args.overwrite_results,
    )

    observer = Observer()
    # Schedule a watch for each root
    for root in watch_roots:
        if root.exists():
            observer.schedule(handler, path=str(root), recursive=args.recursive)
            print(f"\n[observer] scheduled: {root}")

    observer.start()

    # Enqueue pre-existing files
    _initial_scan_and_enqueue(watch_roots, args.recursive, handler)

    # Graceful shutdown
    def _shutdown(signum=None, frame=None):
        print("\n[exit] stopping observer...")
        observer.stop()
        observer.join()
        print("[exit] shutting down workers...")
        executor.shutdown(wait=True, cancel_futures=False)
        print("[exit] done.")
        raise SystemExit(0)

    signal.signal(signal.SIGINT, _shutdown)  # Ctrl+C
    signal.signal(signal.SIGTERM, _shutdown)  # kill/stop

    try:
        while True:
            time.sleep(1.0)
    except KeyboardInterrupt:
        _shutdown()

if __name__ == "__main__":
    main()
