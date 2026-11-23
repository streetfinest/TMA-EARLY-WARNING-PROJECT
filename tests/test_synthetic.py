"""Independent small-data checks of count arithmetic and episode boundaries."""
import numpy as np
import pandas as pd
from group3_climatology.baseline import forecast_table
from group3_climatology.historical import drought_episodes


def mini_data():
    rows=[]
    for year,spi in [(2011,-2.1),(2012,.3),(2013,-1.7),(2014,.2),(2015,-2.2)]:
        rows.append({'district_id':'0001','region':'Synthetic','district':'Test','month':pd.Timestamp(year,4,1),
                     'spi3_gamma_ref1981_2010':spi,'severe_spi3_this_month':int(spi<=-1.5)})
    return pd.DataFrame(rows)


def test_unsmoothed_probability():
    d=mini_data()
    f=forecast_table(d,2015,2015,leads=(1,2,3))
    assert len(f)==3
    assert (f.historical_valid_years==4).all()
    assert (f.historical_severe_years==2).all()
    assert np.allclose(f.predicted_probability,.5)


def test_episode_requires_consecutive_months():
    rows=[]
    for year,mon,spi in [(2020,1,-2),(2020,2,-1.6),(2020,4,-2.1),(2020,5,-.2),(2020,6,-1.7)]:
        rows.append({'district_id':'0001','district':'Test','region':'Synthetic',
                     'month':pd.Timestamp(year,mon,1),'spi3_gamma_ref1981_2010':spi})
    events=drought_episodes(pd.DataFrame(rows))
    assert sorted(events.duration_months)==[1,1,2]
