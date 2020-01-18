import pandas as pd
import matplotlib.pyplot as plt
import shapefile
import utm
import os
import numpy as np
import cartopy.crs as ccrs
import cartopy.feature as cf
import cartopy.io.img_tiles as tile
import matplotlib as mpl
from common import *

# Figure settings
# mpl.rc('savefig', dpi=300)
mpl.rc('figure', figsize=[15,15])
mpl.rc('figure', titlesize=22)
mpl.rc('xtick', labelsize=40)
mpl.rc('ytick', labelsize=20)
mpl.rc('ytick', right=True)
mpl.rc('legend', fontsize=22)
mpl.rc('axes', labelsize=40)


def read_stations(filename):
    df = pd.read_csv(filename, sep='\t', index_col=1)
    columns = ['Number','Name','Latitude','Longitude','Altitude']
    df.columns = columns
    df.index.name = 'id'
    return df


def read_shapefile():
    # Plot shapefile
    shpFilePath = '../project_data/Narayani_catchment/watershed.shp '
    listx=[]
    listy=[]
    sf = shapefile.Reader(shpFilePath)
    for sr in sf.shapeRecords():
        for xNew,yNew in sr.shape.points:
            listx.append(xNew)
            listy.append(yNew)
    plt.plot(listx,listy)


def location_discharge():
    stations = []
    for root, dirs, files in os.walk(DISDIR):
        stations = dirs
        break

    df = pd.DataFrame(columns = ['Name','Latitude','Longitude'])
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
    return df


if __name__ == '__main__':
    FIGDIR = '../figures/'

    df = read_stations('../project_data/station_loc.txt')
    df2 = location_discharge()
    latitude = []
    longitude = []
    shpFilePath = '../project_data/Narayani_catchment/watershed.shp '
    sf = shapefile.Reader(shpFilePath)
    for sr in sf.shapeRecords():
        for x,y in sr.shape.points:
            # print(x,y)
            # Eastward shift of data
            lat,lon = utm.to_latlon(x+3650,y,45,'R')
            latitude.append(lat)
            longitude.append(lon)
    ax = plt.axes(projection=ccrs.PlateCarree())
    terrain = tile.Stamen('terrain-background')
    ax.add_image(terrain, 8)
    ax.plot(longitude, latitude,transform=ccrs.PlateCarree())
    ax.set_extent([82.8,86,27.2,29.5])

    # Maybe change to one of the qualitative colormaps. Paired?
    colors = ['red','yellow','blue','orange','purple']
    # Plot meteorological and discharge stations
    for i,color in zip(df.index,colors):
        ax.plot(df.loc[i,'Longitude'],df.loc[i,'Latitude'], label=df.loc[i,'Name'], color=color,marker='s', markersize=10)
    for i,color in zip(df2.index,colors):
        ax.plot(df2.loc[i,'Longitude'],df2.loc[i,'Latitude'], label=df2.loc[i,'Name'], color=color, marker='o',markersize=10)

    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                  linewidth=1, color='gray', alpha=0.8, linestyle='--')
    gl.xlabels_top = False
    gl.ylabels_left = False
    # Plot location of Katmandu for reference

    ax.scatter(85.322274, 27.703203,label='Katmandu', color='k',marker='x')
    from cartopy.mpl.gridliner import LONGITUDE_FORMATTER, LATITUDE_FORMATTER

    # gl.xlabel('Longitude')
    # gl.ylabel('Latitude')
    gl.xformatter = LONGITUDE_FORMATTER
    gl.yformatter = LATITUDE_FORMATTER

    ax.coastlines()
    plt.legend(loc='upper right')


    plt.savefig(FIGDIR+'stations.png', bbox_inches="tight")
