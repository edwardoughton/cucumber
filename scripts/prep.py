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
from dataprep.clean import clean_lat_long
from tqdm import tqdm

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')


def process_cells():
    """

    """
    ##load the first database
    filename = 'ELEMENTOS_AUTORIZATORIOS_EN_SERVICIO.shp'
    directory = os.path.join(
        DATA_RAW,
        'Data Request (GIS)',
        'Network info (Existing)',
        'Mobile Broadband',
        'Estaciones Base Servicio Móvil',
        'Antenas Autorizadas en Servicio'
    )
    path = os.path.join(directory, filename)
    df = gpd.read_file(path, crs='epsg:4326')#[:10]

    df = df[['geometry', 'NOMBRE_RZ', 'FRECUENCIA', 'TECNOLOGIA']]
    df.columns = ['geometry', 'operator', 'frequency', 'technology']
    df['source'] = filename

    ##load the second database
    filename = 'CELLID_2021_03.shp'
    directory = os.path.join(
        DATA_RAW,
        'Data Request (GIS)',
        'Network info (Existing)',
        'Mobile Broadband',
        'Estaciones Base Servicio Móvil',
        'Cell ID STI - 2021-03'
    )
    path = os.path.join(directory, filename)
    df2 = gpd.read_file(path, crs='epsg:4326')#[:10]

    df2['frequency'] = ''
    df2 = df2[['geometry', 'NOMBRE_EMP', 'frequency', 'TITE_COD' ]]
    df2.columns = ['geometry', 'operator', 'frequency', 'technology']
    df2['source'] = filename

    df = df.append(df2)
    df.to_file(os.path.join(DATA_INTERMEDIATE, 'cellular', 'cells.shp'))


def process_fixed_broadband():
    """

    """
    dir_out = os.path.join(DATA_INTERMEDIATE, 'fixed')

    if not os.path.exists(dir_out):
        os.makedirs(dir_out)

    directory = os.path.join(
        DATA_RAW,
        'Data Request (GIS)',
        'Network info (Existing)',
        'Fiber Optic Backbone',
        'Trazados y Nodos Red Troncal FO',
    )

    filename = 'Celeo Redes.gdb'
    path = os.path.join(directory, 'Celeo Redes', filename)
    layers = fiona.listlayers(path)
    for layer in layers:
        gdf = gpd.read_file(path, layer=layer)
        path_out = os.path.join(dir_out, 'celo_redes_{}.shp'.format(layer))
        gdf.to_file(path_out, crs='epsg:4326')

    filename = 'Century.gdb'
    path = os.path.join(directory, 'Century Link', filename)
    layers = fiona.listlayers(path)
    for layer in layers:
        gdf = gpd.read_file(path, layer=layer)
        path_out = os.path.join(dir_out, 'century_link_{}.shp'.format(layer))
        gdf.to_file(path_out, crs='epsg:4326')

    filename = 'Claro_KML_Enlaces_of138.gdb'
    path = os.path.join(directory, 'Claro', filename)
    layers = fiona.listlayers(path)
    for layer in layers:
        gdf = gpd.read_file(path, layer=layer)
        path_out = os.path.join(dir_out, 'claro_kml_enlaces_of138_{}.shp'.format(layer))
        gdf.to_file(path_out, crs='epsg:4326')

    filename = 'Claro_KML_Sitios_of138.gdb'
    path = os.path.join(directory, 'Claro', filename)
    layers = fiona.listlayers(path)
    for layer in layers:
        gdf = gpd.read_file(path, layer=layer)
        path_out = os.path.join(dir_out, 'Claro_KML_Sitios_of138_{}.shp'.format(layer))
        gdf.to_file(path_out, crs='epsg:4326')

    filename = 'Claro_KML_Sitios_of138.gdb'
    path = os.path.join(directory, 'Claro', filename)
    layers = fiona.listlayers(path)
    for layer in layers:
        gdf = gpd.read_file(path, layer=layer)
        path_out = os.path.join(dir_out, 'Claro_KML_Sitios_of138_{}.shp'.format(layer))
        gdf.to_file(path_out, crs='epsg:4326')

    filename = 'PAR_PNTL_kml.gdb'
    path = os.path.join(directory, 'Conductividad Austral', filename)
    layers = fiona.listlayers(path)
    for layer in layers:
        gdf = gpd.read_file(path, layer=layer)
        path_out = os.path.join(dir_out, 'PAR_PNTL_kml_{}.shp'.format(layer))
        gdf.to_file(path_out, crs='epsg:4326')

    filename = 'PAR_PNTL_kml.gdb'
    path = os.path.join(directory, 'Conductividad Austral', filename)
    layers = fiona.listlayers(path)
    for layer in layers:
        gdf = gpd.read_file(path, layer=layer)
        path_out = os.path.join(dir_out, 'PAR_PNTL_kml_{}.shp'.format(layer))
        gdf.to_file(path_out, crs='epsg:4326')

    filename = 'Of Cir 138-C-2018 ESA FO.gdb'
    path = os.path.join(directory, 'ENTEL', filename)
    layers = fiona.listlayers(path)
    for layer in layers:
        gdf = gpd.read_file(path, layer=layer)
        path_out = os.path.join(dir_out, 'Of Cir 138-C-2018 ESA FO_{}.shp'.format(layer))
        gdf.to_file(path_out, crs='epsg:4326')


def grep_folder():

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

    for file_type in file_types:

        for folder in folders:

            network_type = os.path.basename(folder)

            print('--Working on {} with {}'.format(file_type, network_type))

            search_path = os.path.join(directory, network_type)

            for path in Path(search_path).rglob('*{}'.format(file_type)):

                # if os.path.exists(path_out):
                #     continue

                if file_type == '.gdb':
                    layers = fiona.listlayers(path)
                    for layer in layers:
                        gdf = gpd.read_file(path, layer=layer)
                        filename = '{}_{}'.format(
                            os.path.basename(os.path.splitext(path)[0]),
                            layer
                        )
                        path_out = os.path.join(folder, filename + '.shp')
                        gdf.to_file(path_out)

                try:
                    gdf = gpd.read_file(path, crs='epsg:4328')
                    path_out = os.path.join(folder, os.path.basename(path) + '.shp')
                    gdf.to_file(path_out)
                except:
                    print('path failed: {}'.format(path))


if __name__ == "__main__":

    # #manual function
    # process_cells()

    # #manual function
    # process_fixed_broadband()

    #automated search and extract
    grep_folder()
