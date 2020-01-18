import pandas as pd
import hyd as hyd
import met as met
from common import *

# Convert station information
met.convert_stations(OUTDIR + 'met_stations.csv')
hyd.convert_stations(OUTDIR + 'hyd_stations.csv')

# Convert station data
met.convert_data(OUTDIR + 'prec.csv','prec')
met.convert_data(OUTDIR + 'temp.csv','temp')
hyd.convert_data(OUTDIR + 'discharge.csv')
