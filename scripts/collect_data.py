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
    )

    folders = [
        os.path.join(DATA_INTERMEDIATE, 'Mobile Broadband'),
        os.path.join(DATA_INTERMEDIATE, 'Fiber Optic Backbone'),
        # os.path.join(DATA_INTERMEDIATE, 'Fixed Broadband'),

    ]

    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)

    excl_files = [
        'dbf', '.prj', '.cpg', '.shx'#, ''
        # '', '.gdbtablx', '.zip', '.gdbtable', '.freelist', '.gdbindexes',
        # '.idx', '.xlsx', '.CPG', '.qpj', '.spx', '.lyr', '.mxd', '.KMZ',
        # '.mpk', '.atx', '.lock', '.sbx', '.kmz', '.rar'
        ]

    files_included = set()
    files_not_included = set()
    file_extensions_excluded = set()

    exclusions = [
        # 'MMOO',
        # '138',
        # 'CHILE Division Regional',
        # 'Enlaces_MMOO_2019_kmz',
        # 'Nodos_oficio_138_emailv2',
    ]


    for path in Path(directory).rglob('*'):

        if 'mobile' in str(path).lower():
            folder = 'Mobile Broadband'
        elif 'fiber' in str(path).lower():
            folder = 'Fiber Optic Backbone'
        else:
            folder = 'unknown'

        file_extension = os.path.splitext(path)[1].lower()
        file_name = os.path.basename(path)

        # if not file_name == 'Of Cir 138-C-2018 ESA FO.kml':
        #     continue

        if any(excp in file_name for excp in exclusions):
                continue

        if file_extension == '.gdb':
            layers = fiona.listlayers(path)
            for layer in layers:
                gdf = gpd.read_file(path, layer=layer)
                filename = '{}_{}'.format(
                    os.path.basename(os.path.splitext(path)[0]),
                    layer
                )
                path_out = os.path.join(DATA_INTERMEDIATE, folder, filename + '.shp')
                gdf.to_file(path_out, crs='epsg:4326')
                files_included.add(file_name)
                continue

        elif file_extension == '.kml':

            gpd.io.file.fiona.drvsupport.supported_drivers['KML'] = 'rw'

            try:
                gdf = gpd.read_file(path, driver='KML')
            except:
                files_not_included.add(file_name)
                continue

            if 'Point' in [i for i in gdf['geometry'].geom_type]:
                points = gdf.loc[gdf['geometry'].geom_type == 'Point']
                path_out = os.path.join(DATA_INTERMEDIATE, folder, file_name + '_points' + '.shp')
                points.to_file(path_out, crs='epsg:4326')
                files_included.add(file_name)
            elif 'LineString' in [i for i in gdf['geometry'].geom_type]:
                linestrings = gdf.loc[gdf['geometry'].geom_type == 'LineString']
                path_out = os.path.join(DATA_INTERMEDIATE, folder, file_name + '_lines' + '.shp')
                linestrings.to_file(path_out, crs='epsg:4326')
                files_included.add(file_name)
            else:
                files_not_included.add(file_name)

        elif file_extension == '.shp':
            filename = os.path.basename(path)[:-4]
            try:
                gdf = gpd.read_file(path, crs='epsg:4326')
            except:
                files_not_included.add(file_name)
                continue
            path_out = os.path.join(DATA_INTERMEDIATE, folder,  filename + '.shp')
            gdf.to_file(path_out, crs='epsg:4326')
            files_included.add(file_name)

        else:
            # print(any(file_extension for word in excl_files))
            if file_extension in excl_files:
                print(file_extension)
                file_extensions_excluded.add(file_name)
                continue
            files_not_included.add(file_name)
            continue

    output = pd.DataFrame({
        'files_included': pd.Series(list(files_included)),
        'files_not_included': pd.Series(list(files_not_included)),
        'file_extensions_excluded': pd.Series(list(file_extensions_excluded)),
    })

    path = os.path.join(DATA_INTERMEDIATE, 'file_inclusions_and_exclusions.csv')
    output.to_csv(path, index=False)

if __name__ == "__main__":

    #automated search and extract
    grep_folder()
