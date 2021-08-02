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
from shapely.geometry import LineString, shape, MultiPoint, mapping
import networkx as nx
from glob import glob
import random

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')


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
    nodes = []
    edges = []
    all_fiber_nodes = []

    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'existing_network', 'Fiber Optic Backbone')
    files = os.listdir(folder)#[:20]

    for filename in files:

        # if not filename == 'RED GAS ANDES.shp':
        #     continue

        if os.path.splitext(filename)[1] == '.shp':

            path = os.path.join(folder, filename)
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
                    nodes.append({
                        'type': 'Feature',
                        'geometry': mapping(routing_structure['geometry']),
                        'properties': {
                            'filename': filename
                        }
                    })

                elif routing_structure['geometry'].geom_type == 'LineString':

                    edges.append({
                        'type': 'Feature',
                        'geometry': mapping(routing_structure['geometry']),
                        'properties': {
                            'filename': filename
                        }
                    })

                    estimated_nodes = get_nodes(routing_structure)

                    for estimated_node in estimated_nodes:
                        all_fiber_nodes.append({
                            'type': 'Feature',
                            'geometry': estimated_node,
                            'properties': {
                                'filename': filename
                            }
                        })

                else:
                    print('Did not recognize stated geometry type {}'.format(
                        routing_structure['geometry'].geom_type))

    if len(nodes) == 0 or len(edges) == 0:
        return

    all_fiber_nodes = all_fiber_nodes + nodes

    nodes = gpd.GeoDataFrame.from_features(nodes, crs='epsg:3857')
    nodes = nodes.to_crs('epsg:4326')
    nodes.to_file(os.path.join(folder, '..', 'fiber_nodes.shp'), crs='epsg:4326')

    edges = gpd.GeoDataFrame.from_features(edges, crs='epsg:3857')
    edges = edges.to_crs('epsg:4326')
    edges.to_file(os.path.join(folder, '..', 'fiber_edges.shp'), crs='epsg:4326')

    all_fiber_nodes = gpd.GeoDataFrame.from_features(all_fiber_nodes, crs='epsg:3857')
    all_fiber_nodes = all_fiber_nodes.to_crs('epsg:4326')
    all_fiber_nodes.to_file(os.path.join(folder, 'all_fiber_nodes.shp'), crs='epsg:4326')

    # path = os.path.join(DATA_INTERMEDIATE, 'CHL', 'national_outline.shp')
    # national_outline = gpd.read_file(path, crs='epsg:4326')

    # output = gpd.overlay(output, national_outline, how='intersection')

    # output.to_file(os.path.join(folder, 'nodes.shp'), crs='epsg:4326')


def get_nodes(routing_structure):
    """

    """
    new_routing_nodes = []

    points_num = int(round(routing_structure['geometry'].length / 250))

    line = routing_structure['geometry']
    new_routing_nodes = MultiPoint([line.interpolate((i/points_num),
        normalized=True) for i in range(1, points_num)])

    return list(new_routing_nodes)


def subset_fiber_by_region(iso3, level):
    """
    Split by region.

    """
    filename = 'regions_{}_{}.shp'.format(level, iso3)
    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'regions')
    path = os.path.join(folder, filename)
    regions = gpd.read_file(path, crs='epsg:4326')#[:1]
    regions = regions.loc[regions.is_valid]

    types = ['fiber_nodes', 'fiber_edges']

    for filetype in types:

        folder = os.path.join(DATA_INTERMEDIATE, iso3, 'existing_network', filetype)

        if not os.path.exists(folder):
            os.makedirs(folder)

        path = os.path.join(folder + '.shp')
        fiber = gpd.read_file(path, crs='epsg:4326')

        for idx, region in tqdm(regions.iterrows(), total=regions.shape[0]):

            GID_id = region["GID_{}".format(level)]

            filename = filetype + '_' + GID_id + '.shp'
            path = os.path.join(folder, filename)

            if os.path.exists(path):
                continue

            geo_region = gpd.GeoDataFrame(geometry=gpd.GeoSeries(region['geometry']),
                crs='epsg:4326')

            fiber_subset = gpd.overlay(fiber, geo_region, how='intersection')

            if len(fiber_subset) > 0:

                fiber_subset.to_file(path, crs='epsg:4326')


def subset_mobile_assets_by_region(iso3, level):
    """
    Split by region.

    """
    filename = 'regions_{}_{}.shp'.format(level, iso3)
    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'regions')
    path = os.path.join(folder, filename)
    regions = gpd.read_file(path, crs='epsg:4326')#[:1]
    regions = regions.loc[regions.is_valid]

    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'sites', 'by_region')
    if not os.path.exists(folder):
        os.makedirs(folder)

    filenames = [
        'CELLID_2021_03.shp',
        'ELEMENTOS_AUTORIZATORIOS_EN_SERVICIO.shp'
    ]

    for filename in filenames:

        path_in = os.path.join(DATA_INTERMEDIATE, iso3, 'existing_network',
            'Mobile Broadband', filename)
        assets = gpd.read_file(path_in, crs='epsg:4326')#[:1]

        for idx, region in tqdm(regions.iterrows(), total=regions.shape[0]):

            GID_id = region["GID_{}".format(level)]

            combined_filename = filename[:-4] + '_' + GID_id + '.shp'
            path_out = os.path.join(DATA_INTERMEDIATE, iso3, 'existing_network',
                'sites', combined_filename)

            if os.path.exists(path_out):
                continue

            geo_region = gpd.GeoDataFrame(geometry=gpd.GeoSeries(region['geometry']),
                crs='epsg:4326')

            subsetted_assets = gpd.overlay(assets, geo_region, how='intersection')

            if len(subsetted_assets) > 0:

                subsetted_assets.to_file(path_out, crs='epsg:4326')


def process_sites(iso3, level, cells_per_site):
    """
    Create sites LUT.

    """
    filename = 'regions_{}_{}.shp'.format(level, iso3)
    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'regions')
    path = os.path.join(folder, filename)
    regions = gpd.read_file(path, crs='epsg:4326')#[:1]
    regions = regions.loc[regions.is_valid]

    backhaul_lut = get_backhaul_lut(iso3, 'LAC', '2025')

    output = []

    for idx, region in tqdm(regions.iterrows(), total=regions.shape[0]):

        GID_level = 'GID_{}'.format(level)
        GID_id = region[GID_level]

        sites_2G = 0
        sites_3G = 0
        sites_4G = 0
        total_sites = 0

        filename = 'CELLID_2021_03_' + GID_id + '.shp'
        path = os.path.join(DATA_INTERMEDIATE, iso3, 'sites', 'by_region', filename)

        if os.path.exists(path):

            cells = gpd.read_file(path, crs='epsg:4326')#[:10]

            for idx, point in cells.iterrows():

                if point['geometry'].intersects(region['geometry']):

                    if '2G' in point['TITE_COD']:
                        sites_2G += 1
                    if '3G' in point['TITE_COD']:
                        sites_3G += 1
                    if '4G' in point['TITE_COD']:
                        sites_4G += 1

            sites_2G = round(sites_2G / cells_per_site)
            sites_3G = round(sites_3G / cells_per_site)
            sites_4G = round(sites_4G / cells_per_site)
            total_sites = sites_2G + sites_3G + sites_4G

        backhaul_estimates = estimate_backhaul(total_sites, backhaul_lut)

        output.append({
            'GID_0': region['GID_0'],
            GID_level: GID_id,
            'sites_2G': sites_2G,
            'sites_3G': sites_3G,
            'sites_4G': sites_4G,
            'total_estimated_sites': total_sites,
            'backhaul_fiber': backhaul_estimates['backhaul_fiber'],
            'backhaul_copper': backhaul_estimates['backhaul_copper'],
            'backhaul_wireless': backhaul_estimates['backhaul_wireless'],
            'backhaul_satellite': backhaul_estimates['backhaul_satellite'],
        })

    output = pd.DataFrame(output)

    filename = 'sites.csv'
    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'sites')
    output.to_csv(os.path.join(folder, filename), index=False)

    return output


def get_backhaul_lut(iso3, region, year):
    """

    """
    interim = []

    path = os.path.join(BASE_PATH, 'raw', 'gsma', 'backhaul.csv')
    backhaul_lut = pd.read_csv(path)
    backhaul_lut = backhaul_lut.to_dict('records')

    for item in backhaul_lut:
        if region == item['Region'] and int(item['Year']) == int(year):
            interim.append({
                'tech': item['Technology'],
                'percentage': int(item['Value']),
            })

    output = {}

    preference = [
        'fiber',
        'copper',
        'microwave',
        'satellite'
    ]

    perc_so_far = 0

    for tech in preference:
        for item in interim:
            if tech == item['tech'].lower():
                perc = item['percentage']
                output[tech] = (perc + perc_so_far) / 100
                perc_so_far += perc

    return output


def estimate_backhaul(total_sites, backhaul_lut):

    output = {}

    backhaul_fiber = 0
    backhaul_copper = 0
    backhaul_wireless = 0
    backhaul_satellite = 0

    for i in range(1, int(round(total_sites)) + 1):

        num = random.uniform(0, 1)

        if num <= backhaul_lut['fiber']:
            backhaul_fiber += 1
        elif backhaul_lut['fiber'] < num <= backhaul_lut['copper']:
            backhaul_copper += 1
        elif backhaul_lut['copper'] < num <= backhaul_lut['microwave']:
            backhaul_wireless += 1
        elif backhaul_lut['microwave'] < num:
            backhaul_satellite += 1

    output['backhaul_fiber'] = backhaul_fiber
    output['backhaul_copper'] = backhaul_copper
    output['backhaul_wireless'] = backhaul_wireless
    output['backhaul_satellite'] = backhaul_satellite

    return output


if __name__ == "__main__":

    iso3 = 'CHL'
    level = 3

    print('Subsetting road network by region')
    subset_road_network_by_region(iso3, level)

    print('Processing fiber')
    process_fiber()

    print('Subsetting fiber network by region')
    subset_fiber_by_region(iso3, level)

    print('Gathering mobile infrastructure assets')
    subset_mobile_assets_by_region(iso3, level)

    print('Processing sites')
    cells_per_site = 3
    process_sites(iso3, level, cells_per_site)
