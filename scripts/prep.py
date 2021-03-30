"""
Process and convert infrastructure data.

Written by Ed Oughton.

March 2021

"""
import os
import configparser
import json
import pandas as pd
import geopandas as gpd
from dataprep.clean import clean_lat_long
from tqdm import tqdm

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')


def process_cells(path):
    """

    """
    df = pd.read_csv(path, encoding= 'unicode_escape')

    df['x'] = df['lon'].str.replace(',', '.')
    df['y'] = df['lat'].str.replace(',', '.')

    # df['x'] = '-' + df['x']
    # df['y'] = '-' + df['y']

    df = clean_lat_long(df, lat_col="x", long_col="y", split=True)

    df = df[['x_clean', 'y_clean']]

    # df = df.dropna()

    gdf = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.x_clean, df.y_clean), crs='epsg:4326')[:1000]

    gdf.to_file(os.path.join(DATA_INTERMEDIATE, 'cellular', 'cells.shp'))

    df.to_csv(os.path.join(DATA_INTERMEDIATE, 'cellular', 'cells.csv'), index=False)


if __name__ == "__main__":

    # path = os.path.join(DATA_RAW, 'cells.csv')
    # process_cells(path)
