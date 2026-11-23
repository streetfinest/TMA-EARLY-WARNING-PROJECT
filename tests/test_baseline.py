"""Reproducibility and no-look-ahead checks for the unweighted baseline."""
import numpy as np
import pandas as pd
import pytest
from group3_climatology.baseline import forecast_table, climatology_snapshot,inspect_forecast
from group3_climatology.data import load_data, audit_data
from group3_climatology.evaluation import score_forecasts,validation_threshold,evaluation_by_period
from group3_climatology.historical import drought_episodes,northern_case_study

@pytest.fixture(scope='module')
def data():return load_data()

@pytest.fixture(scope='module')
def predictions(data):return forecast_table(data)


def test_integrity(data):
    report=audit_data(data)
    assert report['district_month_records']==81000
    assert report['districts']==150
    assert report['valid_spi3']==80700
    assert report['severe_spi3_months']==4364
    assert report['duplicate_district_month']==0


def test_real_probability(data,predictions):
    row=inspect_forecast(predictions,'Nanyumbu','2020-04-01',3).iloc[0]
    assert int(row.historical_severe_years)==4
    assert int(row.historical_valid_years)==39
    assert np.isclose(row.predicted_probability,4/39)
    assert str(row.issue_month.date())=='2020-01-01'
    assert row.observed_spi3 <= -1.5
    assert (predictions.latest_used_month_upper_bound < predictions.issue_month).all()


def test_all_leads_agree(predictions):
    p=predictions.pivot(index=['district_id','target_month'],columns='horizon_months',values='predicted_probability')
    assert np.allclose(p[1],p[2]) and np.allclose(p[2],p[3])
    assert (predictions.groupby(['district_id','target_month']).size()==3).all()
    assert len(predictions)==59400


def test_snapshot(data):
    p=climatology_snapshot(data)
    assert len(p)==1800
    assert p.probability.between(0,1).all()
    assert (p.D <= p.N).all()


def test_episodes(data):
    severe=drought_episodes(data,-1.5)
    assert len(severe)==2859
    assert severe.duration_months.max()==7
    assert int(severe.duration_months.sum())==4364


def test_alert_threshold_from_validation_only(predictions):
    cutoff,scan=validation_threshold(predictions)
    assert np.isclose(cutoff,.055)
    assert scan.iloc[0].threshold==cutoff
    assert scan['threshold'].nunique()>=30


def test_case_study_scores(predictions):
    sample=predictions[predictions.target_month.dt.year.between(2020,2022)&(predictions.horizon_months==1)]
    m=score_forecasts(sample,.055)
    assert m['forecasts']==5400 and m['severe_district_months']==150
    assert m['true_alerts']==84 and m['false_alerts']==2307
    assert m['missed_drought_months']==66 and m['correct_nonalerts']==2943
    assert np.isclose(m['roc_auc'],.5501701587301588)
    assert np.isclose(m['brier_score'],.0287444660002697)
    assert np.isclose(m['recall'],.56)


def test_future_observations_do_not_change_previous_forecast(data):
    original=forecast_table(data,2020,2020)
    history_cut=data[data.month.dt.year<=2020]
    truncated=forecast_table(history_cut,2020,2020)
    pd.testing.assert_frame_equal(original,truncated)


def test_malformed_labels_rejected(data):
    modified=data.copy()
    first=modified['spi3_gamma_ref1981_2010'].first_valid_index()
    modified.loc[first,'severe_spi3_this_month'] = 1 - modified.loc[first,'severe_spi3_this_month']
    with pytest.raises(ValueError,match='Quality-control failure'):
        audit_data(modified)


def test_northern_case_severe_zero(data):
    table=northern_case_study(data)
    assert len(table)==6
    assert table['months_with_severe_spi3'].sum()==0


def test_invalid_forecast_horizon(data):
    with pytest.raises(ValueError,match='lead times'):
        forecast_table(data,2020,2020,(12,))
