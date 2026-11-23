"""Run the Seasonal Climatology pipeline without opening JupyterLab."""
import argparse
import json
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from group3_climatology.pipeline import run_pipeline

p=argparse.ArgumentParser(description='Rebuild Seasonal Climatology research outputs.')
p.add_argument('--input',type=Path,default=ROOT/'data/processed/tma_baseline_inputs.csv.gz')
p.add_argument('--out',type=Path,default=ROOT/'outputs')
p.add_argument('--no-plots',action='store_true')
args=p.parse_args()
result=run_pipeline(args.input,args.out,plots=not args.no_plots)
print(json.dumps(result,indent=2,default=str))
