"""Regenerate the compact project input from an original TMA data archive."""
import argparse
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from group3_climatology.data import extract_core_data
p=argparse.ArgumentParser()
p.add_argument('archive',type=Path)
p.add_argument('--allow-different-checksum',action='store_true')
a=p.parse_args()
data=extract_core_data(a.archive,verify_hash=not a.allow_different_checksum)
print(f'Extracted {len(data):,} records from {a.archive}')
