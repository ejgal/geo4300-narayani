import pandas as pd
import os
import numpy as np
import matplotlib.pyplot as plt
from common import *

def convert_stations(outfile):
    """
    Convert information about meteorological stations to .csv.
    """
    df = pd.read_csv(INDIR + 'station_loc.txt', sep='\t', index_col=1)
    columns = ['Number','Name','Latitude','Longitude','Altitude']
    df.columns = columns
    df = df.drop('Number', axis=1)
    df.index.name = 'id'
    df.to_csv(outfile)
    return df




def get_year(filepath):
    """
    Find year of station data, based on file ending.
    """
    year = int(filepath.split('.')[-1].strip())
    if year < 30:
        year = int('20{:02}'.format(year))
    else:
        year = int('19{:02}'.format(year))
    return year


def convert_data(outfile, variable):
    """
    Convert all data of type variable to nice csv files.

    Variable: temp or prec
    """
    stations = []
    frames = []
    folder = INDIR + variable + '/'
    for root, dirs, files in os.walk(folder):
        stations = dirs
        break
    for station in stations:
        df = load_station(station, variable,folder)
        frames.append(df)
    df = pd.concat(frames, axis=1)
    df.to_csv(outfile)


def load_station(station, variable, folder):
    """
    Read data of type variable from one station.
    """
    path = folder + station + '/'
    frames = []
    files = os.listdir(path)
    for file in files:
        filepath = path + file
        if variable == 'prec':
            df = load_precipitation(filepath,station)
        elif variable == 'temp':
            df = load_temperature(filepath,station)
        # df = load_df(filepath, station)
        frames.append(df)
    df = pd.concat(frames)
    return df



def load_temperature(filepath, station):
    """
    Load one file containing temperature data
    """
    # Remove leading zero in station name
    name1 = '{}_max'.format(station.lstrip('0'))
    name2 = '{}_min'.format(station.lstrip('0'))
    names = [name1,name2]
    df = pd.read_csv(filepath, skiprows=2, skipfooter=1,engine='python' ,delim_whitespace=True, index_col=0, header=None,names=names)
    df.index.name = 'date'

    # Replace T and DNA with NaN
    df = df.replace("T",np.nan)
    df = df.replace("DNA", np.nan)
    year = get_year(filepath)
    # Convert to numeric
    for name in names:
        df[name] = pd.to_numeric(df[name])
    # Replace -99.9 with NaN
    df = df.replace(-99.9, np.nan)
    year = get_year(filepath)
    # index = pd.to_datetime(year*1000 + 5, format='%Y%j')
    df.index = pd.to_datetime(year*1000 + df.index, format='%Y%j')
    return df


def load_precipitation(filepath, station):
    """
    Load one file containing precipitation data
    """
    # name = 'precip_{}'.format(station)
    name = station.lstrip('0')
    df = pd.read_csv(filepath, skipfooter=1,engine='python' ,delim_whitespace=True, index_col=0, header=None,names=[name])
    df.index.name = 'date'
    # Replace DNA with NaN
    df = df.replace("DNA", np.nan)
    # T -> 0.2
    df = df.replace("T",0.2)
    year = get_year(filepath)
    # Convert to numeric
    df[name] = pd.to_numeric(df[name])
    # Replace -99.9 with NaN
    df = df.replace(-99.9, np.nan)
    # # Half of 1969 is missing values, and rest is zero. Missing data?
    # if year == 1969:
    #     df = df.replace(0, np.nan)
    # index = pd.to_datetime(year*1000 + 5, format='%Y%j')
    df.index = pd.to_datetime(year*1000 + df.index, format='%Y%j')
    return df



if __name__ == '__main__':
    # Convert station information
    convert_stations('met_stations.csv')

    # Convert station data
    convert_data(OUTDIR + 'prec','prec')
    convert_data(OUTDIR + 'temp','temp')
