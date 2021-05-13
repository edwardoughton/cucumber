"""
Process settlement layer and explore fiber routing methods.

Written by Ed Oughton.

May 2021

"""
import os
import configparser
import math
import pandas as pd
import geopandas as gpd
from tqdm import tqdm
from shapely.geometry import LineString, shape, MultiPoint

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')


def process_country_shapes(iso3):
    """
    Creates a single national boundary for the desired country.

    """
    path = os.path.join(DATA_INTERMEDIATE, iso3)

    if os.path.exists(os.path.join(path, 'national_outline.shp')):
        return 'Already completed national outline processing'

    if not os.path.exists(path):
        #Creating new directory
        os.makedirs(path)

    shape_path = os.path.join(path, 'national_outline.shp')

    #Loading all country shapes
    path = os.path.join(DATA_RAW, 'gadm36_levels_shp', 'gadm36_0.shp')
    countries = gpd.read_file(path)

    #Getting specific country shape
    single_country = countries[countries.GID_0 == iso3]

    #Adding ISO country code and other global information
    glob_info_path = os.path.join(DATA_RAW, 'global_information.csv')
    load_glob_info = pd.read_csv(glob_info_path, encoding = "ISO-8859-1")
    single_country = single_country.merge(
        load_glob_info,left_on='GID_0', right_on='ISO_3digit')

    #Exporting processed country shape
    single_country.to_file(shape_path, driver='ESRI Shapefile')

    return


def process_regions(iso3, level):
    """
    Function for processing the lowest desired subnational regions for the
    chosen country.

    """
    regions = []

    for regional_level in range(1, level + 1):

        filename = 'regions_{}_{}.shp'.format(regional_level, iso3)
        folder = os.path.join(DATA_INTERMEDIATE, iso3, 'regions')
        path_processed = os.path.join(folder, filename)

        if os.path.exists(path_processed):
            continue

        if not os.path.exists(folder):
            os.mkdir(folder)

        filename = 'gadm36_{}.shp'.format(regional_level)
        path_regions = os.path.join(DATA_RAW, 'gadm36_levels_shp', filename)
        regions = gpd.read_file(path_regions)

        #Subsetting regions
        regions = regions[regions.GID_0 == iso3]

        try:
            #Writing global_regions.shp to file
            regions.to_file(path_processed, driver='ESRI Shapefile')
        except:
            print('Unable to write {}'.format(filename))
            pass

    return


def load_original_data(path):
    """

    """
    df = pd.read_excel (path, sheet_name='Entidades Censo')
    df = df[['Longitud', 'Latitud', 'Region', 'Comuna', 'Localidad']]

    data = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(
        df.Longitud, df.Latitud))

    filename = 'Entidades Censales Coberturas 2020-3.shp'
    folder = os.path.join(DATA_INTERMEDIATE, 'census_entities')
    if not os.path.exists(folder):
        os.makedirs(folder)
    data.to_file(os.path.join(folder, filename), crs='epsg:4326')


def subset_census_entities_by_region(iso3, level):
    """
    Write out census entities by local statistical unit.

    """
    filename = 'Entidades Censales Coberturas 2020-3.shp'
    folder = os.path.join(DATA_INTERMEDIATE, 'census_entities')
    path = os.path.join(folder, filename)
    census_entities = gpd.read_file(path, crs='epsg:4326')

    filename = 'regions_{}_{}.shp'.format(level, iso3)
    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'regions')
    path = os.path.join(folder, filename)
    regions = gpd.read_file(path, crs='epsg:4326')#[:1]
    regions = regions.loc[regions.is_valid]

    for idx, region in tqdm(regions.iterrows(), total=regions.shape[0]):

        GID_id = region["GID_{}".format(level)]

        path = os.path.join(DATA_INTERMEDIATE, 'census_entities', GID_id + '.shp')

        if os.path.exists(path):
            continue

        geo_region = gpd.GeoDataFrame(geometry=gpd.GeoSeries(region['geometry']),
            crs='epsg:4326')

        settlements = gpd.overlay(census_entities, geo_region, how='intersection')

        if len(settlements) > 0:

            settlements.to_file(path, crs='epsg:4326')

    print('Completed subsetting of census entities')


def subset_road_network_by_region(iso3, level):
    """
    Write out road network by local statistical unit.

    """
    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'road_network')
    if not os.path.exists(folder):
        os.makedirs(folder)

    filename = 'gis_osm_roads_free_1.shp'
    path = os.path.join(DATA_RAW, 'osm', filename)
    road_network = gpd.read_file(path, crs='epsg:4326')#[:1]

    filename = 'regions_{}_{}.shp'.format(level, iso3)
    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'regions')
    path = os.path.join(folder, filename)
    regions = gpd.read_file(path, crs='epsg:4326')#[:1]
    regions = regions.loc[regions.is_valid]

    for idx, region in tqdm(regions.iterrows(), total=regions.shape[0]):

        GID_id = region["GID_{}".format(level)]

        path = os.path.join(DATA_INTERMEDIATE, iso3, 'road_network', GID_id + '.shp')

        if os.path.exists(path):
            continue

        geo_region = gpd.GeoDataFrame(geometry=gpd.GeoSeries(region['geometry']),
            crs='epsg:4326')

        road_edges = gpd.overlay(road_network, geo_region, how='intersection')

        if len(road_edges) > 0:

            road_edges.to_file(path, crs='epsg:4326')

    print('Completed subsetting of census entities')


def process_fiber():
    """
    Process fiber layers and export.

    """
    output = []

    files = os.listdir(os.path.join(DATA_INTERMEDIATE, 'Fiber Optic Backbone'))#[:20]

    for filename in files:

        # if not filename == 'RED GAS ANDES.shp':
        #     continue

        if os.path.splitext(filename)[1] == '.shp':

            path = os.path.join(DATA_INTERMEDIATE, 'Fiber Optic Backbone', filename)
            data = gpd.read_file(path, crs='epsg:4326')
            data = data[['geometry']].reset_index()
            try:
                data = data.to_crs('epsg:3857')
            except:
                print('Could not transform {}'.format(path))
                continue

            for idx, routing_structure in data.iterrows():

                if math.isnan(routing_structure['geometry'].length):
                    continue

                if routing_structure['geometry'].geom_type == 'Point':
                    output.append({
                        'type': 'Feature',
                        'geometry': routing_structure['geometry'],
                        'properties': {
                            'filename': filename
                        }
                    })
                elif routing_structure['geometry'].geom_type == 'LineString':

                    nodes = get_nodes(routing_structure)

                    for node in nodes:
                        output.append({
                            'type': 'Feature',
                            'geometry': node,
                            'properties': {
                                'filename': filename
                            }
                        })
                else:
                    print('Did not recognize stated geometry type {}'.format(
                        routing_structure['geometry'].geom_type))

    if len(output) == 0:
        return

    output = gpd.GeoDataFrame.from_features(output, crs='epsg:3857')
    output = output.to_crs('epsg:4326')

    folder = os.path.join(DATA_INTERMEDIATE, 'CHL', 'existing_network')
    if not os.path.exists(folder):
        os.makedirs(folder)
    output.to_file(os.path.join(folder, 'nodes.shp'), crs='epsg:4326')


def get_nodes(routing_structure):
    """

    """
    new_routing_nodes = []

    points_num = int(round(routing_structure['geometry'].length / 1000))

    line = routing_structure['geometry']
    new_routing_nodes = MultiPoint([line.interpolate((i/points_num),
        normalized=True) for i in range(1, points_num)])

    return list(new_routing_nodes)


if __name__ == "__main__":

    iso3 = 'CHL'
    level = 3

    ### Processing country boundary ready to export
    process_country_shapes(iso3)

    ### Processing regions ready to export
    process_regions(iso3, level)

    filename = 'Entidades Censales Coberturas 2020-3.xlsx'
    folder = os.path.join(DATA_RAW, 'Solicitud 9 de abril', '6')
    path = os.path.join(folder, filename)

    if not os.path.exists(path):
        load_original_data(path)

    # subset_census_entities_by_region(iso3, level)

    # subset_road_network_by_region(iso3, level)

    process_fiber()
