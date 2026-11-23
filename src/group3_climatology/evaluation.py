"""Forecast probability scoring and retrospective warning diagnostics."""
from __future__ import annotations
import numpy as np
import pandas as pd
from sklearn.metrics import roc_auc_score, average_precision_score, brier_score_loss
from .config import VALIDATION_YEARS


def score_forecasts(forecasts: pd.DataFrame, threshold: float | None = None) -> dict:
    if forecasts.empty:
        raise ValueError('Cannot score an empty forecast sample.')
    y = forecasts['observed_severe'].to_numpy(dtype=int)
    p = forecasts['predicted_probability'].to_numpy(dtype=float)
    if not np.isfinite(p).all() or not ((0 <= p) & (p <= 1)).all():
        raise ValueError('Probability inputs must be finite values between zero and one.')
    result = {
        'forecasts': int(len(y)), 'severe_district_months': int(y.sum()),
        'severe_event_rate': float(y.mean()), 'mean_predicted_probability': float(p.mean()),
        'brier_score': float(brier_score_loss(y,p)),
        'roc_auc': float(roc_auc_score(y,p)) if np.unique(y).size == 2 else float('nan'),
        'average_precision': float(average_precision_score(y,p)) if y.sum() > 0 else float('nan'),
    }
    if threshold is not None:
        if not 0 <= threshold <= 1:
            raise ValueError('Alert threshold must be in [0,1].')
        predicted = p >= threshold
        tp = int(np.sum(predicted & (y == 1)))
        fp = int(np.sum(predicted & (y == 0)))
        fn = int(np.sum((~predicted) & (y == 1)))
        tn = int(np.sum((~predicted) & (y == 0)))
        precision = tp/(tp+fp) if tp+fp else 0.0
        recall = tp/(tp+fn) if tp+fn else 0.0
        f2 = 5*precision*recall/(4*precision+recall) if 4*precision+recall else 0.0
        result.update({
            'warning_threshold': float(threshold),
            'true_alerts': tp, 'false_alerts': fp,
            'missed_drought_months': fn, 'correct_nonalerts': tn,
            'warnings': tp+fp, 'precision': precision, 'recall': recall,
            'f2_score': f2,
            'false_alerts_per_100_forecasts': 100*fp/len(y),
            'false_alert_rate': fp/(fp+tn) if fp+tn else float('nan'),
        })
    return result


def validation_threshold(forecasts: pd.DataFrame, start: int = VALIDATION_YEARS[0],
                         end: int = VALIDATION_YEARS[1]) -> tuple[float, pd.DataFrame]:
    """Choose a warning threshold only on earlier validation targets (one lead)."""
    subset = forecasts[(forecasts['target_month'].dt.year.between(start,end))
                       & (forecasts['horizon_months'] == 1)]
    if subset.empty:
        raise ValueError('No validation forecasts in the requested period.')
    rows = []
    for threshold in np.round(np.arange(.01,.301,.005),3):
        result = score_forecasts(subset,float(threshold))
        rows.append({'threshold':float(threshold),
                     'f2_score':result['f2_score'], 'precision':result['precision'],
                     'recall':result['recall'], 'true_alerts':result['true_alerts'],
                     'false_alerts':result['false_alerts']})
    ranked = pd.DataFrame(rows).sort_values(['f2_score','false_alerts','threshold'],
                                           ascending=[False,True,False]).reset_index(drop=True)
    return float(ranked.loc[0,'threshold']),ranked


def evaluation_by_period(forecasts: pd.DataFrame, threshold: float) -> pd.DataFrame:
    periods = {
        'validation_2015_2018':(2015,2018),
        'diagnostic_2019':(2019,2019),
        'case_study_2020_2022':(2020,2022),
        'retrospective_2023_2025':(2023,2025),
        'retrospective_2020_2025':(2020,2025),
    }
    rows = []
    for name,(start,end) in periods.items():
        for lead in (1,2,3):
            sample = forecasts[(forecasts['target_month'].dt.year.between(start,end))
                               & forecasts['horizon_months'].eq(lead)]
            rows.append({'period':name, 'lead_months':lead, **score_forecasts(sample,threshold)})
    return pd.DataFrame(rows)


def onset_warnings(forecasts: pd.DataFrame, threshold: float,
                   start: int = 2020, end: int = 2022, lead: int = 1) -> dict:
    sample = forecasts[(forecasts['target_month'].dt.year.between(start,end))
                       & (forecasts['horizon_months'] == lead)]
    onsets = sample[sample['severe_onset'].eq(1)]
    return {'observed_new_severe_onsets':int(len(onsets)),
            'onset_months_with_warning':int((onsets['predicted_probability'] >= threshold).sum()),
            'onset_months_without_warning':int((onsets['predicted_probability'] < threshold).sum())}


def monthly_case_study(forecasts: pd.DataFrame, start: int = 2020,
                      end: int = 2022, lead: int = 1) -> pd.DataFrame:
    sample = forecasts[(forecasts['target_month'].dt.year.between(start,end))
                       & forecasts['horizon_months'].eq(lead)]
    return sample.groupby('target_month',as_index=False).agg(
        observed_severe_districts=('observed_severe','sum'),
        observed_fraction=('observed_severe','mean'),
        mean_baseline_probability=('predicted_probability','mean'),
        district_count=('district_id','nunique'))
