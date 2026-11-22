#!/usr/bin/env python3
"""Reproduce the TMA P06 *retrospective* scientific analyses locally.

Examples:
    python run_project.py --mode all
    python run_project.py --mode history
    python run_project.py --mode impacts
    python run_project.py --mode forecasting
    python run_project.py --mode verify

Dependencies: pip install -r requirements.txt
NOTE: This is NOT a live operational forecasting service.
"""
from pathlib import Path
from datetime import datetime,timezone
import argparse,hashlib,json,os,subprocess,sys,time

ROOT=Path(__file__).resolve().parent
SCRIPTS=ROOT/'src'/'engine'
OUT=ROOT/'outputs'
LOGS=OUT/'logs'

TASKS={
 'history':['historical.py','--input',str(ROOT/'data/processed/stage1_validated_district_month.csv'),
            '--out',str(OUT/'historical'),'--geo',str(ROOT/'data/geography/NBS_2022_districts.gpkg')],
 'impacts':['impact_validation.py','--data-zip',str(ROOT/'data/raw/TMA(1).zip'),
            '--stage2',str(OUT/'historical/stage2_monthly_indices_quality_flagged.csv'),
            '--out',str(OUT/'impact_validation')],
 'case':['case_study.py'],
 'forecasting':['TMA_P06_Stage5_Models.py','--root',str(ROOT),'--output',str(OUT/'forecasting')],
 'optimization':['optimization.py']
}
REQUIRED={
 'history':[OUT/'historical/stage2_monthly_indices_quality_flagged.csv'],
 'impacts':[OUT/'impact_validation/stage3_ndvi_district_month_anomalies.csv'],
 'case':[OUT/'case_study/stage4_district_season_comparison.csv'],
 'forecasting':[OUT/'forecasting/stage5_performance_metrics.csv'],
 'optimization':[OUT/'optimization/stage6_performance_metrics.csv'],
}

def run(name):
    LOGS.mkdir(parents=True,exist_ok=True)
    for dep in {'impacts':['history'],'case':['impacts'],'forecasting':['impacts'],'optimization':['forecasting']}.get(name,[]):
        for path in REQUIRED[dep]:
            if not path.exists():
                raise FileNotFoundError(f'{name} requires {dep}; run --mode all, or run {dep} first: {path}')
    args=[sys.executable,"-u",str(SCRIPTS/TASKS[name][0]),*TASKS[name][1:]]
    env=os.environ.copy();env['TMA_PROJECT_ROOT']=str(ROOT);env['TMA_STAGE6_ROOT']=str(ROOT)
    started=time.monotonic();print('RUNNING',name,flush=True)
    with (LOGS/f'{name}.log').open('w',encoding='utf8') as log:
        proc=subprocess.run(args,cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
    if proc.returncode!=0:
        print('FAILED',name,'see',LOGS/f'{name}.log',flush=True)
        raise RuntimeError(f'{name} failed (exit={proc.returncode})')
    for item in REQUIRED[name]:
        if not item.is_file(): raise RuntimeError(f'Expected output missing: {item}')
    print('COMPLETED',name,round(time.monotonic()-started,1),'seconds',flush=True)

def verify():
    import pandas as pd, numpy as np
    master=pd.read_csv(ROOT/'data/standardized/district_month_master.csv',parse_dates=['month'],dtype={'district_code':str})
    assert len(master)==81000 and master.district_code.nunique()==150
    assert not master.duplicated(['district_code','month']).any()
    assert master.chirps3_rain_mm.notna().all() and (master.chirps3_rain_mm>=0).all()
    original_idx=pd.read_csv(ROOT/'data/processed/stage2_monthly_indices_quality_flagged.csv',dtype={'district_id':str},parse_dates=['month'])
    regenerated=pd.read_csv(OUT/'historical/stage2_monthly_indices_quality_flagged.csv',dtype={'district_id':str},parse_dates=['month'])
    assert len(regenerated)==len(original_idx)==81000
    assert not regenerated.duplicated(['district_id','month']).any()
    verify_cols=['spi3_verified','spei3_loglogistic_verified','water_balance_score3_sensitivity']
    for c in verify_cols:
       a=original_idx[c].to_numpy(float); b=regenerated[c].to_numpy(float)
       assert np.array_equal(np.isnan(a),np.isnan(b)),f'Missing values changed: {c}'
       err=np.nanmax(np.abs(a-b));assert err<2e-6,(c,err)
       print(f'{c}: {int(np.isfinite(b).sum()):,} values; max difference {err:.2g}')
    nd=pd.read_csv(OUT/'impact_validation/stage3_ndvi_district_month_anomalies.csv',dtype={'district_id':str},parse_dates=['month'])
    assert len(nd)==21432 and nd.district_id.nunique()==76
    a=pd.read_csv(ROOT/'results/stage3_index_vegetation_metrics.csv')
    b=pd.read_csv(OUT/'impact_validation/stage3_index_vegetation_metrics.csv')
    keys=['period','lead_months','cohort','index']
    j=a.merge(b,on=keys,suffixes=('_saved','_new'),validate='one_to_one')
    assert len(j)==len(a)==len(b)
    for c in ['matched_pairs','districts','spearman_rho','roc_auc_vegetation_stress']:
       l=j[c+'_saved'].to_numpy(float);r=j[c+'_new'].to_numpy(float)
       assert np.allclose(l,r,atol=2e-6,equal_nan=True),(c,np.nanmax(np.abs(l-r)))
    print('Stage 3 matched metrics reproducible')
    if (OUT/'forecasting/stage5_performance_metrics.csv').exists():
        c=pd.read_csv(OUT/'forecasting/stage5_performance_metrics.csv')
        assert len(c)==72 and set(c.lead_months)=={1,2,3}
        assert c.brier.between(0,1).all()
        print('Forecasting models:',c.model.nunique(),'targets:',c.target.nunique(),'valid performance rows:',len(c))
    summary={'timestamp_utc':datetime.now(timezone.utc).isoformat(),'checks':'PASS',
      'rows':len(master),'districts':master.district_code.nunique(),
      'spi_valid':int(regenerated.spi3_verified.notna().sum()),
      'spei_valid':int(regenerated.spei3_loglogistic_verified.notna().sum()),
      'vegetation_rows':len(nd),'NOTE':'No full independent external validation or live forecasting.'}
    (OUT/'phase3_verification.json').write_text(json.dumps(summary,indent=2))
    print('VERIFIED: all Phase 3 numerical checks passed')

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--mode',choices=['all','history','impacts','case','forecasting','optimization','verify'],default='all')
    args=parser.parse_args()
    if args.mode=='all':
      for name in ['history','impacts','case','forecasting','optimization']:run(name)
      verify()
    elif args.mode=='verify':verify()
    else:run(args.mode)
