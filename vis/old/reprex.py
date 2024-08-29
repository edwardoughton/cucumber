"""
Plot spatial data. 

Written by Ed Oughton.

June 2024.

"""
import os
# import sys
import configparser

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), '..', 'scripts', 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']
VIS = os.path.join(BASE_PATH, '..', 'vis', 'figures')

import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import Point
import random 

example = []
for i in range(0,20):
    example.append({
        'geometry': Point(
                random.randrange(-200,1000),
                random.randrange(-200,100)
                ).buffer(100),
        'properties': {
            'emissions': random.randrange(100)
        }
    }) 

geo_df = gpd.GeoDataFrame.from_features(example)

fig, (ax1, ax2, ax3) = plt.subplots(3, figsize=(7, 9), layout='constrained')

bins = [0,10,20,30,40,50,60,70,80,90,100]
geo_df['bin'] = pd.cut(geo_df['emissions'], bins=bins)

base = geo_df.plot(
    column='bin', 
    ax=ax1, 
    legend=True,
    legend_kwds={"label": "Emissions (xx/x)", "loc": "lower left", 'size': 6} 
    )

# ax1.legend(loc='lower left')
path = os.path.join(VIS, 'demo.png')
fig.savefig(path, dpi=300)

