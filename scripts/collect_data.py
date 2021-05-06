"""
Process and convert infrastructure data.

Written by Ed Oughton.

March 2021

"""
import os
import configparser
from pathlib import Path
import json
import pandas as pd
import fiona
import geopandas as gpd
# from dataprep.clean import clean_lat_long
from tqdm import tqdm
from re import search

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')


def grep_folder():
    """
    Load in all desired shapes.

    """
    directory = os.path.join(
        DATA_RAW,
        'Data Request (GIS)',
        'Network info (Existing)',
    )

    folders = [
        os.path.join(DATA_INTERMEDIATE, 'Mobile Broadband'),
        os.path.join(DATA_INTERMEDIATE, 'Fiber Optic Backbone'),
        os.path.join(DATA_INTERMEDIATE, 'Fixed Broadband'),
    ]

    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)

    file_types = [
        '.shp',
        '.gdb'
    ]

    exlusions = [
        'MMOO',
        '138',
        'CHILE Division Regional',
        'Enlaces_MMOO_2019_kmz',
        'Nodos_oficio_138_emailv2',
    ]

    for file_type in file_types:

        for folder in folders:

            network_type = os.path.basename(folder)

            search_path = os.path.join(directory, network_type)

            for path in Path(search_path).rglob('*{}'.format(file_type)):

                file_name = os.path.basename(path)

                # if not file_name == 'Claro_KML_Enlaces_of138.gdb':
                #     continue

                if any(excp in file_name for excp in exlusions):
                     continue

                if file_type == '.gdb':
                    layers = fiona.listlayers(path)
                    for layer in layers:
                        gdf = gpd.read_file(path, layer=layer)
                        filename = '{}_{}'.format(
                            os.path.basename(os.path.splitext(path)[0]),
                            layer
                        )
                        path_out = os.path.join(folder, filename + '.shp')
                        gdf.to_file(path_out, crs='epsg:4326')
                        continue

                try:
                    ext = os.path.basename(path)[-4:]
                    filename = os.path.basename(path)[:-4]
                    gdf = gpd.read_file(path, crs='epsg:4326')
                    path_out = os.path.join(folder,  filename + ext)
                    gdf.to_file(path_out, crs='epsg:4326')

                except:
                    print('path failed: {}'.format(path))



if __name__ == "__main__":

    #automated search and extract
    grep_folder()
