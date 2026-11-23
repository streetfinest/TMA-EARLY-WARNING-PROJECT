"""Complete, reproducible Seasonal Climatology analysis pipeline."""
from __future__ import annotations
import json
from pathlib import Path
import pandas as pd
from .config import INPUT, OUTPUT, GEOGRAPHY
from .data import audit_data, load_data
from .historical import historical_tables,drought_episodes,northern_case_study
from .baseline import forecast_table,climatology_snapshot
from .evaluation import validation_threshold,evaluation_by_period,onset_warnings,monthly_case_study
from .plots import plot_annual,plot_districts,plot_monthly,plot_episode_duration,plot_case_study,plot_confusion,plot_geographic


def run_pipeline(input_path:Path = INPUT,output_path:Path = OUTPUT,plots:bool=True)->dict:
    output_path=Path(output_path)
    for folder in ['tables','predictions','metrics','figures','maps']:
        (output_path/folder).mkdir(parents=True,exist_ok=True)
    data=load_data(input_path)
    qc=audit_data(data,strict=True)
    with (output_path/'metrics/data_quality.json').open('w',encoding='utf-8') as f:
        json.dump(qc,f,indent=2)
    tables=historical_tables(data)
    for name,df in tables.items():
        df.to_csv(output_path/f'tables/{name}_drought_history.csv',index=False)
    severe=drought_episodes(data,-1.5)
    drought=drought_episodes(data,-1.0)
    severe.to_csv(output_path/'tables/severe_drought_episode_register.csv',index=False)
    drought.to_csv(output_path/'tables/drought_episode_register.csv',index=False)
    northern=northern_case_study(data)
    northern.to_csv(output_path/'tables/northern_2021_2022_rainfall.csv',index=False)
    forecasts=forecast_table(data)
    forecasts.to_csv(output_path/'predictions/seasonal_climatology_forecasts_2015_2025.csv',index=False)
    snapshot=climatology_snapshot(data)
    snapshot.to_csv(output_path/'predictions/district_month_climatology_as_of_2019.csv',index=False)
    threshold,scan=validation_threshold(forecasts)
    scan.to_csv(output_path/'metrics/validation_threshold_search.csv',index=False)
    evaluation=evaluation_by_period(forecasts,threshold)
    evaluation.to_csv(output_path/'metrics/model_evaluation.csv',index=False)
    timeline=monthly_case_study(forecasts)
    timeline.to_csv(output_path/'tables/2020_2022_observed_vs_forecast.csv',index=False)
    base_row=evaluation[(evaluation.period=='case_study_2020_2022') & (evaluation.lead_months==1)].iloc[0].to_dict()
    result = {
        'data':qc, 'historical':{
            'severe_district_months':qc['severe_spi3_months'],
            'severe_episodes':len(severe),
            'drought_episodes_spi3_le_minus1':len(drought),
            'longest_severe_episode_months':int(severe.duration_months.max()),
        },
        'validation_selected_warning_threshold':threshold,
        'case_study_2020_2022':base_row,
        'onset_2020_2022':onset_warnings(forecasts,threshold)
    }
    with (output_path/'metrics/run_summary.json').open('w',encoding='utf-8') as f:
        json.dump(result,f,indent=2,default=lambda o:float(o) if hasattr(o,'item') else str(o))
    if plots:
        fig=plot_annual(tables['annual'],output_path/'figures/annual_severe_frequency.png');fig.clf()
        fig=plot_districts(tables['district'],output_path/'figures/highest_frequency_districts.png');fig.clf()
        fig=plot_monthly(tables['calendar_month'],output_path/'figures/calendar_month_frequency.png');fig.clf()
        fig=plot_episode_duration(severe,output_path/'figures/severe_episode_durations.png');fig.clf()
        fig=plot_case_study(timeline,output_path/'figures/2020_2022_observed_vs_baseline.png');fig.clf()
        fig=plot_confusion(base_row,output_path/'figures/2020_2022_warning_confusion.png');fig.clf()
        if GEOGRAPHY.exists():
            fig=plot_geographic(tables['district'],GEOGRAPHY,output_path/'maps/historical_severe_frequency_map.png')
            if fig is not None: fig.clf()
        import matplotlib.pyplot as plt
        plt.close('all')
    return result
