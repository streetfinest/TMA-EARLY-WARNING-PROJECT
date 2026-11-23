"""Execute the single research notebook and stop on any failing cell."""
from pathlib import Path
import argparse
import nbformat
from nbclient import NotebookClient

ROOT = Path(__file__).resolve().parents[1]
NOTEBOOK = ROOT / "notebooks" / "Seasonal_Climatology_Research.ipynb"
parser = argparse.ArgumentParser(description="Execute Seasonal Climatology research notebook.")
parser.add_argument("--no-save", action="store_true")
parser.add_argument("--timeout", type=int, default=240)
args = parser.parse_args()
notebook = nbformat.read(NOTEBOOK, as_version=4)
NotebookClient(notebook,timeout=args.timeout,kernel_name="python3",
               resources={"metadata":{"path":str(ROOT)}},allow_errors=False).execute()
if not args.no_save:
    nbformat.write(notebook,NOTEBOOK)
print("Seasonal Climatology notebook executed successfully.")
