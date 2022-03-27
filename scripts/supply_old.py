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
    regions = gpd.read_file(path, crs='epsg:4326')#[:2]
    regions = regions.loc[regions.is_valid]

    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'sites', 'by_region')
    if not os.path.exists(folder):
        os.makedirs(folder)

    path_in = os.path.join(DATA_INTERMEDIATE, iso3, 'existing_network',
        'Mobile Broadband', 'CELLID_2021_03.shp')
    assets = gpd.read_file(path_in, crs='epsg:4326')#[:2000]

    total_sites = []

    for idx, region in tqdm(regions.iterrows(), total=regions.shape[0]):

        GID_id = region["GID_{}".format(level)]

        combined_filename = GID_id + '.shp'
        path_out = os.path.join(DATA_INTERMEDIATE, iso3, #'existing_network',
            'sites', 'by_region', combined_filename)

        # if os.path.exists(path_out):
        #     continue

        combined_filename =  'unbuffered' + '_' + GID_id + '.shp'
        path_unbuffered = os.path.join(DATA_INTERMEDIATE, iso3,
            'sites', 'by_region', combined_filename)

        if os.path.exists(path_unbuffered):
            subsetted_assets = gpd.read_file(path_unbuffered, crs='epsg:4326')#[:2000]
        else:
            geo_region = gpd.GeoDataFrame(geometry=gpd.GeoSeries(region['geometry']),
                crs='epsg:4326')
            subsetted_assets = gpd.overlay(assets, geo_region, how='intersection')
            if len(subsetted_assets) > 0:
                unbuffered = subsetted_assets
                unbuffered = unbuffered.to_crs('epsg:4326')
                unbuffered.to_file(path_unbuffered, crs='epsg:4326')

        subsetted_assets = subsetted_assets.to_crs('epsg:3857')

        interim = []

        for idx, asset in subsetted_assets.iterrows():

            asset['geometry'] = asset['geometry'].buffer(5)

            coords = asset['geometry'].representative_point()

            cell_id = '{}_{}_{}_{}_{}'.format(
                asset['TITE_COD'],
                asset['NOMBRE_EMP'],
                coords.x,
                coords.y,
                asset['CBSA_CELL_'],
            )

            interim.append({
                'type': 'Polygon',
                'geometry': asset['geometry'],
                'coords': coords,
                'properties': {
                    'technology': asset['TITE_COD'],
                    'cell_id': cell_id,
                },
            })

        # total_sites = total_sites + interim

        output = []
        seen = set()

        for asset1 in interim:

            polys = []
            cells_2G = 0
            cells_3G = 0
            cells_4G = 0

            cell_id = asset1['properties']['cell_id']

            if cell_id in seen:
                continue
            else:
                seen.add(cell_id)
                polys.append(asset1['coords'])
                if asset1['properties']['technology'] == '2G':
                    cells_2G += 1
                if asset1['properties']['technology'] == '3G':
                    cells_3G += 1
                if asset1['properties']['technology'] == '4G':
                    cells_4G += 1

            for asset2 in interim:

                cell_id = asset2['properties']['cell_id']

                if cell_id in seen:
                    continue

                if asset1['geometry'].intersects(asset2['geometry']):
                    polys.append(asset2['coords'])
                    seen.add(cell_id)
                    if asset2['properties']['technology'] == '2G':
                        cells_2G += 1
                    if asset2['properties']['technology'] == '3G':
                        cells_3G += 1
                    if asset2['properties']['technology'] == '4G':
                        cells_4G += 1

            output.append({
                'type': 'Point',
                'geometry': MultiPoint(polys).representative_point(),
                'properties': {
                    # 'technology': asset1['properties']['technology'],
                    'cells_2G': cells_2G,
                    'cells_3G': cells_3G,
                    'cells_4G': cells_4G,
                },
            })

            total_sites.append({
                'cells_2G': cells_2G,
                'cells_3G': cells_3G,
                'cells_4G': cells_4G,
            })

        if len(output) > 0:

            output = gpd.GeoDataFrame.from_features(output, crs='epsg:3857')

            # geoms = output['geometry'].unary_union

            # output = gpd.GeoDataFrame(geometry=[geoms], crs='epsg:3857')

            # output = output.explode().reset_index(drop=True)

            # output['geometry'] = output['geometry'].representative_point()

            output = output.to_crs('epsg:4326')

            output.to_file(path_out, crs='epsg:4326')

    total_sites = pd.DataFrame(total_sites)
    fold = os.path.join(DATA_INTERMEDIATE, iso3, 'sites', 'by_region')
    total_sites.to_csv(os.path.join(fold, 'total_sites.csv'))


def process_sites(iso3, level):
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

        cells_2G = 0
        cells_3G = 0
        cells_4G = 0

        sites_2G = 0
        sites_3G = 0
        sites_4G = 0

        total_sites = 0

        filename = GID_id + '.shp'
        path = os.path.join(DATA_INTERMEDIATE, iso3, 'sites', 'by_region', filename)

        if os.path.exists(path):

            cells = gpd.read_file(path, crs='epsg:4326')#[:10]

            for idx, point in cells.iterrows():

                if point['geometry'].intersects(region['geometry']):

                    cells_2G += point['cells_2G']
                    cells_3G += point['cells_3G']
                    cells_4G += point['cells_4G']

                    if point['cells_4G'] > 0:
                        sites_4G += 1
                    elif point['cells_3G'] > 0:
                        sites_3G += 1
                    elif point['cells_2G'] > 0:
                        sites_2G += 1

            # sites_2G = round(sites_2G / cells_per_site)
            # sites_3G = round(sites_3G / cells_per_site)
            # sites_4G = round(sites_4G / cells_per_site)
            total_sites = round(sites_2G + sites_3G + sites_4G)

        backhaul_estimates = estimate_backhaul(total_sites, backhaul_lut)

        output.append({
            'GID_0': region['GID_0'],
            GID_level: GID_id,
            'cells_2G': cells_2G,
            'cells_3G': cells_3G,
            'cells_4G': cells_4G,
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

    # print('Subsetting road network by region')
    # subset_road_network_by_region(iso3, level)

    # print('Processing fiber')
    # process_fiber()

    # print('Subsetting fiber network by region')
    # subset_fiber_by_region(iso3, level)

    # print('Gathering mobile infrastructure assets')
    # subset_mobile_assets_by_region(iso3, level)

    print('Processing sites')
    process_sites(iso3, level)
