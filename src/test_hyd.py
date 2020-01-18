import hyd as hyd
import pandas as pd
import numpy as np
import os
from common import *

rtol = 0.01

def test_discharge():
    """
    Run through all discharge data files
    and run check_discharge.
    """
    stations = []
    for root, dirs, files in os.walk(DISDIR):
        stations = dirs
        break
    print(stations)
    for station in stations:
        path = DISDIR + station + '/Daily Discharge/'
        files = os.listdir(path)
        for filename in files:
                filepath = path+filename
                check_discharge(filepath, rtol)



def check_discharge(filepath, rtol):
    """
    Compute min, max and mean value and compare with values from file
    to check that data is loaded correctly.
    """
    df = hyd.load_df_manual(filepath)
    monthly = df.groupby(df.index.month)
    test_df = load_stats(filepath)
    test_df['mintest'] = monthly.min()
    test_df['maxtest'] = monthly.max()
    test_df['meantest'] = monthly.mean()
    x = test_df['min'].values[0]
    for i in test_df.index:
        min = test_df.loc[i,'min']
        max = test_df.loc[i,'max']
        mean = test_df.loc[i,'mean']
        mintest = test_df.loc[i,'mintest']
        maxtest = test_df.loc[i,'maxtest']
        meantest = test_df.loc[i,'meantest']
        test_data = [mintest, maxtest, meantest, min, max, mean]
        hasnan = False
        for data in test_data:
            if np.isnan(data):
                hasnan = True
        if not hasnan:
            assert np.isclose(mintest, min, rtol=rtol)
            assert np.isclose(maxtest, max, rtol=rtol)
            assert np.isclose(meantest, mean, rtol=rtol)
        else:
            print('Cannot test, sinces test data contain nan')

def load_stats(filepath):
    """
    Get min, max and mean discharge values from discharge file
    """

    with open(filepath) as file:
        min = []
        lines = file.readlines()[42:]
        # Split and drop first column containing text and last column containing yearly values
        min = lines[0].split()[1:-1]
        mean = lines[1].split()[1:-1]
        max = lines[2].split()[1:-1]
        df = pd.DataFrame({'min': min,'max': max, 'mean':mean},dtype=np.float64)
        df = df.replace('NA',np.nan)
        for col in ['min', 'mean','max']:
            df[col] = pd.to_numeric(df[col])
        df.index += 1
    return df
