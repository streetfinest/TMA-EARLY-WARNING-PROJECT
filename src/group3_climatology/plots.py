"""Standard figures for the research notebooks."""
from __future__ import annotations
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def save_figure(fig, destination: str | Path):
    path = Path(destination)
    path.parent.mkdir(parents=True,exist_ok=True)
    fig.savefig(path, dpi=150, bbox_inches='tight')
    return fig


def plot_annual(annual: pd.DataFrame, destination: str | Path):
    fig,ax = plt.subplots(figsize=(10,4))
    ax.plot(annual['year'],annual['severe_frequency']*100,lw=1.6)
    ax.axvspan(2020,2022,alpha=.12)
    ax.set(xlabel='Year',ylabel='Severe district-months (%)',
           title='Severe SPI-3 drought frequency in Tanzania, 1981–2025')
    ax.grid(axis='y',alpha=.25)
    return save_figure(fig,destination)


def plot_districts(district: pd.DataFrame,destination: str | Path):
    top=district.nlargest(15,'severe_frequency').sort_values('severe_frequency')
    fig,ax=plt.subplots(figsize=(9,5.8))
    ax.barh(top['district']+' ('+top['region']+')',top['severe_frequency']*100)
    ax.set(xlabel='Share of valid district-months (%)',
           title='15 districts with highest severe SPI-3 frequency')
    ax.grid(axis='x',alpha=.25)
    return save_figure(fig,destination)


def plot_monthly(monthly: pd.DataFrame,destination: str | Path):
    fig,ax=plt.subplots(figsize=(9,3.7))
    ax.bar(monthly['calendar_month'],monthly['severe_frequency']*100)
    ax.set(xlabel='Calendar month',ylabel='Severe district-months (%)',
           title='Monthly seasonal distribution of severe SPI-3 drought',
           xticks=range(1,13))
    ax.grid(axis='y',alpha=.25)
    return save_figure(fig,destination)


def plot_episode_duration(episodes: pd.DataFrame,destination: str | Path):
    fig,ax=plt.subplots(figsize=(8.5,3.6))
    counts=episodes['duration_months'].value_counts().sort_index()
    ax.bar(counts.index,counts.values)
    ax.set(xlabel='Consecutive months',ylabel='Number of severe episodes',
           title='Duration of consecutive severe SPI-3 episodes')
    ax.set_xticks(counts.index)
    ax.grid(axis='y',alpha=.25)
    return save_figure(fig,destination)


def plot_case_study(monthly: pd.DataFrame,destination: str | Path):
    fig,ax=plt.subplots(figsize=(10,4))
    ax.plot(monthly['target_month'],monthly['observed_fraction']*100,
            label='Observed severe SPI-3 (%)',lw=1.8)
    ax.plot(monthly['target_month'],monthly['mean_baseline_probability']*100,
            label='Mean Seasonal Climatology risk (%)',lw=1.8)
    ax.set(xlabel='Target month',ylabel='Share / probability (%)',
           title='Observed drought and climatological risk, 2020–2022')
    ax.grid(axis='y',alpha=.25)
    ax.legend()
    return save_figure(fig,destination)


def plot_confusion(metrics: dict,destination: str | Path):
    matrix=np.array([[metrics['correct_nonalerts'],metrics['false_alerts']],
                     [metrics['missed_drought_months'],metrics['true_alerts']]])
    fig,ax=plt.subplots(figsize=(6,4.7))
    ax.imshow(matrix,cmap='Blues')
    for (i,j),n in np.ndenumerate(matrix):
        ax.text(j,i,f'{int(n):,}',ha='center',va='center',fontsize=13,
                color='white' if n>matrix.max()*.55 else 'black')
    ax.set(xticks=[0,1],yticks=[0,1],xticklabels=['No warning','Warning'],
           yticklabels=['No severe drought','Severe drought'],
           xlabel='Forecast alert',ylabel='Observed outcome',
           title='Retrospective alert classification, 2020–2022')
    return save_figure(fig,destination)


def plot_probability_bins(frame:pd.DataFrame,destination:str | Path):
    f=frame.copy()
    f['band']=pd.cut(f['predicted_probability'],bins=np.linspace(0,1,11),include_lowest=True)
    by=f.groupby('band',observed=True).agg(mean_prediction=('predicted_probability','mean'),
                                           actual_rate=('observed_severe','mean'),
                                           sample_size=('observed_severe','size')).reset_index()
    fig,ax=plt.subplots(figsize=(6,5))
    ax.plot([0,1],[0,1],ls='--',color='#666',lw=1,label='Perfect calibration')
    ax.plot(by['mean_prediction'],by['actual_rate'],marker='o',lw=1.6,label='Observed')
    ax.set(xlim=(0,.35),ylim=(0,.35),xlabel='Forecast probability',
           ylabel='Observed frequency',title='Probability reliability (occupied bins)')
    ax.grid(alpha=.22);ax.legend()
    return save_figure(fig,destination),by


def plot_geographic(district:pd.DataFrame,geo_path:str | Path,destination:str | Path):
    """Optional choropleth using the NBS 2022 administrative geography."""
    try:
        import geopandas as gpd
    except ImportError:
        return None
    g=gpd.read_file(geo_path)
    if 'district_id' not in g.columns:
        raise ValueError('District boundary file has no district_id field.')
    g['district_id']=g['district_id'].astype(str).str.zfill(4)
    a=g.merge(district[['district_id','severe_frequency']],on='district_id',validate='one_to_one')
    if len(a)!=len(district):
        raise ValueError('District-boundary match is incomplete.')
    fig,ax=plt.subplots(figsize=(8,7))
    a.plot(column='severe_frequency',ax=ax,cmap='Blues',legend=True,
           linewidth=.2,edgecolor='#777777',legend_kwds={'label':'Fraction of valid months'})
    ax.set_axis_off();ax.set_title('Historical severe SPI-3 frequency, 1981–2025')
    return save_figure(fig,destination)
