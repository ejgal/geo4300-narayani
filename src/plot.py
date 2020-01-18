import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib as mpl
import seaborn as sns
from common import *
import statsmodels.formula.api as smf

# Plot settings
# mpl.rc('savefig', dpi=300)
mpl.rc('figure', figsize=[10,6])
mpl.rc('figure', titlesize=22)
mpl.rc('xtick', labelsize=20)
mpl.rc('ytick', labelsize=20)
mpl.rc('ytick', right=True)
mpl.rc('legend', fontsize=16)
mpl.rc('axes', labelsize=20)


def monthly_temperature(df):
    """
    Returns dataframe with monthly averaged temperatures, and with a new column
    showing the height of stations.
    """

    monthly = df.groupby(df.index.month).mean()
    monthly.index = monthly.index.map(str)
    monthly = monthly.transpose()
    height = []
    name_height = map_name_height()
    for i in monthly.index:
        station = i.split('_')[0]
        height.append(name_height[station])
    monthly['height'] = height
    tmax = monthly.loc[['Lete_max', 'Pohara_max','Dhunche_max','Lumle_max','Rampur_max'],:]
    tmin = monthly.loc[['Lete_min', 'Pohara_min','Dhunche_min','Lumle_min','Rampur_min'],:]
    return tmin, tmax


def monthly_precipitation(df):
    """
    Returns new dataframe containing total monthly precipitation, and a new
    column showing station height.
    """
    name_height = map_name_height()
    monthly = df.groupby(df.index.month).mean()

    monthly.index = monthly.index.map(str)
    monthly = monthly.transpose()
    height = []
    for i in monthly.index:
        height.append(name_height[i])
    monthly['height'] = height
    return monthly


def load_data():
    prec = pd.read_csv(precipitation, index_col='date')
    prec.index = pd.to_datetime(prec.index)

    temp = pd.read_csv(temperature, index_col='date')
    temp.index = pd.to_datetime(temp.index)

    dis = pd.read_csv(discharge, index_col='date')
    dis.index = pd.to_datetime(dis.index)

    p, t, q = number_to_name(prec, temp, dis)
    return p, t, q


def map_name_height():
    name_height = {}
    with open('../project_data/station_loc.txt') as file:
        for line in file.readlines()[1:-1]:
            line = line.split()
            station = line[2]
            elevation = line[-1]
            name_height[station] = float(elevation)
    return name_height


def number_to_name(p,t,q):
    """
    Changes station numbers to names in dataframes.
    """

    # Precipitation
    df = pd.read_csv(DATADIR + 'met_stations.csv')
    number_name = {}
    for i in df.index:
        number_name[df.loc[i,'id']] = df.loc[i,'Name']

    new_columns = []
    for column in p.columns:
        new_columns.append(number_name[float(column)])
    p.columns = new_columns

    # Temperature
    new_columns = []
    for column in t.columns:
        station = column.split('_')[0]
        prefix = column.split('_')[1]
        newcol = number_name[float(station)] + '_' +prefix
        new_columns.append(newcol)
    t.columns = new_columns

    # Discharge
    df = pd.read_csv(DATADIR + 'hyd_stations.csv')
    for i in df.index:
        number_name[df.loc[i,'id']] = df.loc[i,'Name']
    new_columns = []
    for column in q.columns:
        new_columns.append(number_name[float(column)])
    q.columns = new_columns
    return p,t,q


def plot_timeseries(df,freq,filename):
    df.resample(freq).mean().plot(subplots=True)
    plt.savefig(FIGDIR + filename)


def plot_coverage(df, filename):
    """
    Visualize missing values in dataframe.
    """
    missing = -df.isna()*100
    missing = missing.groupby(df.index.year).mean()
    missing.index.name = 'Year'
    plt.clf()
    plt.figure(figsize = (15,18))
    ax = sns.heatmap(missing, cmap='Blues')
    bottom, top = ax.get_ylim()
    ax.set_ylim(bottom + 0.5, top - 0.5)

    plt.yticks(rotation=0)

    plt.savefig(FIGDIR + filename, bbox_inches="tight")


def lapserate(df, drop=None, indep='height'):
    dfd = df
    if drop:
        for col in drop:
            dfd = dfd.drop(col)
    df = pd.DataFrame(columns=['Lapse rate','error'])
    for i in range(1,13):
        formula = 'Q("{}") ~ {}'.format(i, indep)
        fit = smf.ols(formula, dfd).fit()
        coeff = fit.params[-1]*1000
        CI = fit.conf_int()
        upper = CI.iloc[1,1]*1000
        error = np.abs(upper - coeff)
        df.loc[i, 'Lapse rate'] = coeff
        df.loc[i, 'error'] = error
    return df


def plot_lapserate(df, filename, ylabel, drop=None, indep='height'):
    df = lapserate(df, drop, indep)
    ax = df.plot(marker='o',linestyle='--',yerr='error', capsize=4)
    ax.set_xlabel('Month')
    plt.grid()
    plt.ylabel(ylabel)
    plt.savefig(FIGDIR + filename)
    plt.clf()


if __name__ == '__main__':

    p, t, q = load_data()

    # Lapse rates
    tmin, tmax = monthly_temperature(t)
    plot_lapserate(tmin, 'lapserate_tmin', 'Deegres C / km')
    plot_lapserate(tmax, 'lapserate_tmax', 'Deegres C / km')

    pm = monthly_precipitation(p)
    plot_lapserate(pm, 'lapserate_precipitation', '(mm/day)/km',drop=['Dhunche','Lete'])

    # Plot monthly variations
    # Precipitation
    pm = p[p > 0]
    monthly = pm.groupby(pm.index.month).mean()
    monthly.plot(marker='o')
    plt.grid()
    plt.xlabel('Month')
    plt.ylabel('Precipitation [mm/d]')
    plt.ylim([0,50])
    plt.savefig(FIGDIR + 'daily_precipitation_monthly.png')
    plt.clf()
    qm = q[q > 0]

    # Discharge
    monthly = qm.groupby(qm.index.month).mean()
    monthly.plot(marker='o')
    plt.grid()
    plt.xlabel('Month')
    plt.ylabel('Discharge [m^3/s]')
    plt.savefig(FIGDIR + 'daily_discharge_monthly.png')
    plt.clf()

    # Temperature
    tmin, tmax = monthly_temperature(t)
    tmin = tmin.transpose()
    tmin = tmin.drop('height')
    tmin.plot(marker='o')
    plt.ylim([-3,30])
    plt.xlabel('Month')
    plt.ylabel('Temperature [Deegres C]')
    plt.grid()

    plt.savefig(FIGDIR + 'monthly_average_min_temperature.png')
    plt.clf()

    tmax = tmax.transpose()
    tmax = tmax.drop('height')
    tmax.plot(marker='o', yerr=tmax.std())
    plt.ylim([0,50])
    plt.grid()
    plt.xlabel('Month')
    plt.ylabel('Temperature [Deegres C]')
    plt.savefig(FIGDIR + 'monthly_average_max_temperature.png')

    # Visualize where we are missing data
    plot_coverage(p,'coverage_precipitation.png')
    plot_coverage(t,'coverage_temperature.png')
    plot_coverage(q,'coverage_discharge.png')

    # Plot timeseries
    plot_timeseries(t, 'D', 'temperature.png')
    plot_timeseries(p, 'D', 'precipitation.png')
    plot_timeseries(q, 'D', 'discharge.png')

    # Plot yearly precipitation
    p_yearly = p.groupby(p.index.year).sum()
    p_yearly = p_yearly[p_yearly > 5]
    summary = pd.DataFrame()
    summary['mean'] = p_yearly.mean()
    summary['max'] = p_yearly.max()
    ax = summary.plot(kind='bar', rot=0)
    ax.yaxis.grid(linestyle='--')
    ax.set_title('Yearly precipitation')
    plt.savefig(FIGDIR + 'yearly_precipitation.png')

    # Plot yearly discharge
    q_yearly = q.groupby(q.index.year).sum()
    q_yearly = q_yearly[q_yearly > 0]
    summary = pd.DataFrame()
    summary['mean'] = q_yearly.mean()
    summary['max'] = q_yearly.max()
    ax = summary.plot(kind='bar', rot=0)
    ax.yaxis.grid(linestyle='--')
    ax.set_title('Yearly discharge')
    plt.savefig(FIGDIR + 'yearly_discharge.png')
