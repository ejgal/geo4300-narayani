# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     formats: ipynb,py
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.4'
#       jupytext_version: 1.2.4
# ---

import pandas as pd
import os
import numpy as np
from common import *

def convert_stations(outfile):
    """
    Convert information about hydrological stations to
    .csv. Also add altitude information.
    """
    # Elevation found from dhm.gov.np/hydrological-station at
    # 24.10.19, 15:24
    station_height = {420:198, 445:485,445:485,447:600,450:180}
    stations = []
    for root, dirs, files in os.walk(DISDIR):
        stations = dirs
        break
    df = pd.DataFrame(columns = ['Name','Latitude','Longitude','Altitude'])
    df.index.name = 'id'
    for station in stations:
        path = DISDIR + station + '/Daily Discharge/'
        # Take one random file for each station
        filepath = path + os.listdir(path)[0]
        with open(filepath) as file:
            lines = (file.readlines()[0:3])
            id = int(lines[0].split()[-1])
            name = lines[1].split()[1]
            latline = lines[1].split()[-3:]
            lonline = lines[2].split()[-3:]
            lat = float(latline[0]) + float(latline[1])/60. + float(latline[2])/3600
            lon = float(lonline[0]) + float(lonline[1])/60. + float(lonline[2])/3600
            df.loc[id,'Latitude'] = lat
            df.loc[id,'Longitude'] = lon
            df.loc[id,'Name'] = name
    for key, value in station_height.items():
        df.loc[key,'Altitude'] = value
    df['Latitude'] = df['Latitude'].astype(float).round(3)
    df['Longitude'] = df['Longitude'].astype(float).round(3)
    df.sort_index().to_csv(outfile)



def load_discharge(station):
    """
    Loads data for one station
    """
    path = DISDIR + station + '/Daily Discharge/'
    frames = []
    files = os.listdir(path)
    for filename in files:
        filepath = path+filename
        frames.append(load_df_manual(filepath))
    return pd.concat(frames)

def get_year(filepath):
    with open(filepath) as file:
            year = file.readlines()[4:5][0].split(':')[-1].strip()
    return int(year)


def get_station(filepath):
    with open(filepath) as file:
        station = file.readline().split(':')[-1].strip()
    return station

def load_df_manual(filepath):
    """
    Converts file containing discharge data to a pandas dataframe
    with datetime index.

    Filepath - path to discharge file
    """

    year = get_year(filepath)
    station = get_station(filepath)
    print('Loading data - station: {}, year: {}'.format(station, year))
    column = station
    df = pd.DataFrame(columns=[column])
    df.index.name = 'date'
    months = ['Jan.', 'Feb.','Mar.','Apr.','May','Jun.','Jul.','Aug.','Sep.','Oct.','Nov.', 'Dec.']

    with open(filepath) as file:
        lines = file.readlines()[10:41]
        for line in lines:
            line = line.split()
            day = int(line[0])
            if day == 29:
                if (year % 4 != 0):
                    line.insert(2,np.nan)
            elif day == 30:
                line.insert(2,np.nan)
            elif day == 31:
                for i in (2,4,6,9,11):
                    line.insert(i,np.nan)

            # Special cases
            # missing value station 450, according to mean should be 946
            if (station == '450' and year == 1977 and day == 17):
                line.insert(6,946)
            for month,month_num in zip(months, range(1,len(months)+1)):
                # Construct date
                date = '{}-{:02}-{}'.format(year, month_num, day)
                precip = line[month_num]

                # Check if value is missing
                if precip == 'NA':
                    precip = np.nan
                else:
                    precip = float(precip)

                # Add to new dataframe
                try:
                    date_time = pd.to_datetime(date)
                    df.loc[date_time] = precip
                except ValueError:
                    continue
    return df


def convert_data(outfile):
    """
    Convert discharge data for all stations and store as csv file.
    """
    stations = []
    frames = []
    for root, dirs, files in os.walk(DISDIR):
        stations = dirs
        break
    for station in stations:
        df = load_discharge(station)
        frames.append(df)
    df = pd.concat(frames,axis=1)
    df.to_csv(outfile)


if __name__ == '__main__':
    df = convert_data()
    df.to_csv('discharge.csv')
    convert_stations('hyd_stations.csv')
