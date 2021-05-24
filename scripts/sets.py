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
    # all_data = []

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

                    # estimated_nodes = get_nodes(routing_structure)

                    # for estimated_node in estimated_nodes:
                    #     all_data.append({
                    #         'type': 'Feature',
                    #         'geometry': estimated_node,
                    #         'properties': {
                    #             'filename': filename
                    #         }
                    #     })

                else:
                    print('Did not recognize stated geometry type {}'.format(
                        routing_structure['geometry'].geom_type))

    if len(nodes) == 0 or len(edges) == 0:
        return

    folder = os.path.join(DATA_INTERMEDIATE, 'CHL', 'existing_network')
    if not os.path.exists(folder):
        os.makedirs(folder)

    all_data = all_data + nodes

    nodes = gpd.GeoDataFrame.from_features(nodes, crs='epsg:3857')
    nodes = nodes.to_crs('epsg:4326')
    nodes.to_file(os.path.join(folder, 'nodes.shp'), crs='epsg:4326')

    edges = gpd.GeoDataFrame.from_features(edges, crs='epsg:3857')
    edges = edges.to_crs('epsg:4326')
    edges.to_file(os.path.join(folder, 'edges.shp'), crs='epsg:4326')

    # all_data = gpd.GeoDataFrame.from_features(all_data, crs='epsg:3857')
    # all_data = all_data.to_crs('epsg:4326')
    # all_data.to_file(os.path.join(folder, 'all_data.shp'), crs='epsg:4326')

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


def chop_fiber_by_region(iso3, level):
    """
    Split by region.

    """
    filename = 'regions_{}_{}.shp'.format(level, iso3)
    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'regions')
    path = os.path.join(folder, filename)
    regions = gpd.read_file(path, crs='epsg:4326')#[:1]
    regions = regions.loc[regions.is_valid]

    types = ['nodes', 'edges']

    for filetype in types:

        path = os.path.join(DATA_INTERMEDIATE, iso3, 'existing_network', filetype + '.shp')
        fiber = gpd.read_file(path, crs='epsg:4326')

        for idx, region in tqdm(regions.iterrows(), total=regions.shape[0]):

            GID_id = region["GID_{}".format(level)]

            filename = filetype + '_' + GID_id + '.shp'
            path = os.path.join(DATA_INTERMEDIATE, iso3, 'existing_network', filename)

            if os.path.exists(path):
                continue

            geo_region = gpd.GeoDataFrame(geometry=gpd.GeoSeries(region['geometry']),
                crs='epsg:4326')

            fiber_nodes = gpd.overlay(fiber, geo_region, how='intersection')

            if len(fiber_nodes) > 0:

                fiber_nodes.to_file(path, crs='epsg:4326')


def load_original_data(path):
    """

    """
    df = pd.read_excel (path, sheet_name='Entidades Censo')
    df = df[['Longitud', 'Latitud', 'Region', 'Comuna', 'Localidad', 'Población']]

    data = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(
        df.Longitud, df.Latitud))

    filename = 'Entidades Censales Coberturas 2020-3.shp'
    folder = os.path.join(DATA_INTERMEDIATE, 'CHL', 'census_entidades')
    if not os.path.exists(folder):
        os.makedirs(folder)
    data.to_file(os.path.join(folder, filename), crs='epsg:4326')


def subset_census_entidades_by_region(iso3, level):
    """
    Write out census entidades by local statistical unit.

    """
    filename = 'Entidades Censales Coberturas 2020-3.shp'
    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'census_entidades')
    path = os.path.join(folder, filename)
    census_entities = gpd.read_file(path, crs='epsg:4326')

    filename = 'regions_{}_{}.shp'.format(level, iso3)
    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'regions')
    path = os.path.join(folder, filename)
    regions = gpd.read_file(path, crs='epsg:4326')#[:1]
    regions = regions.loc[regions.is_valid]

    for idx, region in tqdm(regions.iterrows(), total=regions.shape[0]):

        GID_id = region["GID_{}".format(level)]

        path = os.path.join(DATA_INTERMEDIATE, iso3, 'census_entidades', GID_id + '.shp')

        # if os.path.exists(path):
        #     continue

        geo_region = gpd.GeoDataFrame(geometry=gpd.GeoSeries(region['geometry']),
            crs='epsg:4326')

        settlements = gpd.overlay(census_entities, geo_region, how='intersection')

        if len(settlements) > 0:

            settlements.to_file(path, crs='epsg:4326')

    print('Completed subsetting of census entidades')


def subset_localidades_points_by_region(iso3, level):
    """
    Write out census localidades by local statistical unit.

    """
    folder_out = os.path.join(DATA_INTERMEDIATE, iso3, 'census_localidades_points')

    if not os.path.exists(folder_out):
        os.makedirs(folder_out)

    if not os.path.exists(os.path.join(DATA_INTERMEDIATE, iso3, 'census_localidades')):
        os.makedirs(os.path.join(DATA_INTERMEDIATE, iso3, 'census_localidades'))

    filename = 'census_localidades_points.shp'
    path_out = os.path.join(folder_out, filename)

    if not os.path.exists(path_out):

        folder = os.path.join(DATA_RAW, 'Data Request (GIS)', 'Official urban-rural boundaries')
        path = os.path.join(folder, 'OFICIO_10_ZONAS_URBANAS_V3.shp')
        data1 = gpd.read_file(path, crs='epsg:4674')#[:10]
        data1['geotype'] = 'urban'

        folder = os.path.join(DATA_RAW, 'Data Request (GIS)', 'Official urban-rural boundaries')
        path = os.path.join(folder, 'OFICIO_10_LOCALIDAD_RURAL_V3.shp')
        data2 = gpd.read_file(path, crs='epsg:4674')#[:10]
        data2['geotype'] = 'rural'

        polys = data1.append(data2).reset_index()

        polys["unique_id"] = polys.reset_index().index
        polys = polys.to_crs('epsg:4326')
        path = os.path.join(DATA_INTERMEDIATE, iso3, 'census_localidades', 'localidades.shp')
        polys.to_file(os.path.join(path), crs='epsg:4326')

        points = polys.to_crs('epsg:3857')
        points['geometry'] = points['geometry'].centroid
        points = points.to_crs('epsg:4326')
        points.to_file(path_out, crs='epsg:4326')

    else:
        points = gpd.read_file(path_out, crs='epsg:4326')

    filename = 'regions_{}_{}.shp'.format(level, iso3)
    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'regions')
    path = os.path.join(folder, filename)
    regions = gpd.read_file(path, crs='epsg:4326')#[:1]
    regions = regions.loc[regions.is_valid]


    lookup = []

    for idx, region in tqdm(regions.iterrows(), total=regions.shape[0]):

        GID_id = region["GID_{}".format(level)]

        path = os.path.join(folder_out, GID_id + '.shp')

        # if os.path.exists(path):
        #     continue

        geo_region = gpd.GeoDataFrame(geometry=gpd.GeoSeries(region['geometry']),
            crs='epsg:4326')

        localidades_points = gpd.overlay(points, geo_region, how='intersection')

        if len(localidades_points) > 0:
            for idx, item in localidades_points.iterrows():

                lookup.append({
                    'GID_id': GID_id,
                    'unique_id': item['unique_id'],
                    # 'lon': item["geometry"].coords[0][0],
                    # 'lat': item["geometry"].coords[0][1],
                })

            localidades_points.to_file(path, crs='epsg:4326')

    lookup = pd.DataFrame(lookup)
    lookup.to_csv(os.path.join(folder_out, 'lookup.csv'), index=False)

    print('Completed subsetting of census entities')


def subset_localidades_polygons_by_region(iso3, level):
    """
    Write out census localidades polygons by local statistical unit.

    """
    path = os.path.join(DATA_INTERMEDIATE, iso3, 'census_localidades', 'localidades.shp')
    polygons = gpd.read_file(path, crs='epsg:4326')
    polygons = polygons.to_dict('records')

    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'census_localidades_points')
    lookup = pd.read_csv(os.path.join(folder, 'lookup.csv'))
    unique_regions = lookup['GID_id'].unique()

    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'census_localidades')

    lut = {}

    for unique_region in tqdm(list(unique_regions)):

        path = os.path.join(folder, unique_region + '.shp')

        if os.path.exists(path):
            continue

        lst = []
        for idx, item in lookup.iterrows():
            if unique_region == item['GID_id']:
                lst.append(item['unique_id'])
        lut[unique_region] = lst

    for key, values in tqdm(lut.items()):

        filename = key + '.shp'
        path = os.path.join(folder, filename)

        if os.path.exists(path):
            continue

        output = []
        for value in values:
            for poly in polygons:
                if value == poly['unique_id']:
                    output.append({
                        'type': 'Feature',
                        'geometry': poly['geometry'],
                        'properties': {},
                    })

        output = gpd.GeoDataFrame.from_features(output, crs='epsg:4326')

        output.to_file(path, crs='epsg:4326')

    print('Completed subsetting of census entities')


def get_settlements_near_roads(iso3, level):
    """

    """
    folder_fiber = os.path.join(DATA_INTERMEDIATE, iso3, 'existing_network', 'buffered_2km')
    if not os.path.exists(folder_fiber):
        os.makedirs(folder_fiber)

    # folder_under = os.path.join(DATA_INTERMEDIATE, iso3, 'settlements', 'within_2km')
    # if not os.path.exists(folder_under):
    #     os.makedirs(folder_under)

    # folder_over = os.path.join(DATA_INTERMEDIATE, iso3, 'settlements', 'over_2km')
    # if not os.path.exists(folder_over):
    #     os.makedirs(folder_over)
    folder_sets = os.path.join(DATA_INTERMEDIATE, iso3, 'settlements')

    filename = 'regions_{}_{}.shp'.format(level, iso3)
    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'regions')
    path = os.path.join(folder, filename)
    regions = gpd.read_file(path, crs='epsg:4326')#[:1]
    regions = regions.loc[regions.is_valid]

    for idx, region in tqdm(regions.iterrows(), total=regions.shape[0]):

        GID_id = region["GID_{}".format(level)]

        filename = 'edges_' + GID_id + '.shp'
        path = os.path.join(DATA_INTERMEDIATE, iso3, 'existing_network', filename)
        if not os.path.exists(path):
            continue
        edges = gpd.read_file(path, crs='epsg:4326')
        edges = edges.to_crs('epsg:3857')
        edges['geometry'] = edges['geometry'].buffer(2000)
        edges = edges.to_crs('epsg:4326')

        filename = 'nodes_' + GID_id + '.shp'
        path = os.path.join(DATA_INTERMEDIATE, iso3, 'existing_network', filename)
        if not os.path.exists(path):
            continue
        nodes = gpd.read_file(path, crs='epsg:4326')
        nodes = nodes.to_crs('epsg:3857')
        nodes['geometry'] = nodes['geometry'].buffer(2000)
        nodes = nodes.to_crs('epsg:4326')

        fiber = edges.append(nodes)
        fiber = fiber[['geometry']]

        path = os.path.join(DATA_INTERMEDIATE, iso3, 'census_entidades', GID_id + '.shp')
        if not os.path.exists(path):
            continue
        settlements = gpd.read_file(path, crs='epsg:4326')

        settlements_within_2km = gpd.overlay(settlements, fiber, how='intersection')
        settlements_over_2km = gpd.overlay(settlements, fiber, how='difference')

        if len(settlements_within_2km) > 0:

            # settlements_within_2km.drop_duplicates(subset=['Longitud', 'Latitud'])
            # path = os.path.join(folder_under, GID_id + '.shp')
            # settlements_within_2km.to_file(path, crs='epsg:4326')
            settlements_within_2km['distance'] = '<2 km'

        if len(settlements_over_2km) > 0:

            # settlements_over_2km.drop_duplicates(subset=['Longitud', 'Latitud'])
            # settlements_over_2km = settlements_over_2km.loc[
            #     settlements_over_2km['Población'] > 200].reset_index()
            # path = os.path.join(folder_over, GID_id + '.shp')
            # settlements_over_2km.to_file(path, crs='epsg:4326')
            settlements_over_2km['distance'] = '>2 km'

        if len(settlements_within_2km) > 0 and len(settlements_over_2km) > 0:
                all_settlements = settlements_within_2km.append(settlements_over_2km)
        elif len(settlements_within_2km) > 0:
                all_settlements = settlements_within_2km
        elif len(settlements_over_2km) > 0:
            all_settlements = settlements_over_2km

        path = os.path.join(folder_sets, GID_id + '.shp')
        all_settlements.to_file(path, crs='epsg:4326')

        path = os.path.join(folder_fiber, GID_id + '.shp')
        fiber.to_file(path, crs='epsg:4326')


def filter_settlements_far_from_roads(iso3, level):
    """

    """
    folder_fiber = os.path.join(DATA_INTERMEDIATE, iso3, 'existing_network', 'buffered_10km')
    if not os.path.exists(folder_fiber):
        os.makedirs(folder_fiber)

    folder_under = os.path.join(DATA_INTERMEDIATE, iso3, 'settlements', 'within_10km')
    if not os.path.exists(folder_under):
        os.makedirs(folder_under)

    folder_over = os.path.join(DATA_INTERMEDIATE, iso3, 'settlements', 'over_10km')
    if not os.path.exists(folder_over):
        os.makedirs(folder_over)

    filename = 'regions_{}_{}.shp'.format(level, iso3)
    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'regions')
    path = os.path.join(folder, filename)
    regions = gpd.read_file(path, crs='epsg:4326')#[:1]
    regions = regions.loc[regions.is_valid]

    for idx, region in tqdm(regions.iterrows(), total=regions.shape[0]):

        GID_id = region["GID_{}".format(level)]

        filename = 'edges_' + GID_id + '.shp'
        path = os.path.join(DATA_INTERMEDIATE, iso3, 'existing_network', filename)
        if not os.path.exists(path):
            continue
        edges = gpd.read_file(path, crs='epsg:4326')
        edges = edges.to_crs('epsg:3857')
        edges['geometry'] = edges['geometry'].buffer(10000)
        edges = edges.to_crs('epsg:4326')

        filename = 'nodes_' + GID_id + '.shp'
        path = os.path.join(DATA_INTERMEDIATE, iso3, 'existing_network', filename)
        if not os.path.exists(path):
            continue
        nodes = gpd.read_file(path, crs='epsg:4326')
        nodes = nodes.to_crs('epsg:3857')
        nodes['geometry'] = nodes['geometry'].buffer(10000)
        nodes = nodes.to_crs('epsg:4326')

        fiber = edges.append(nodes)

        path = os.path.join(DATA_INTERMEDIATE, iso3, 'settlements', 'over_2km', GID_id + '.shp')
        if not os.path.exists(path):
            continue
        settlements = gpd.read_file(path, crs='epsg:4326')
        settlements = settlements.loc[settlements['Población'] > 200].reset_index()

        if len(settlements) == 0:
            continue

        settlements_within_10km = gpd.overlay(settlements, fiber, how='intersection')
        settlements_over_10km = gpd.overlay(settlements, fiber, how='difference')

        if len(settlements_within_10km) > 0:

            settlements_within_10km.drop_duplicates(subset=['Longitud', 'Latitud'])
            path = os.path.join(folder_under, GID_id + '.shp')
            settlements_within_10km.to_file(path, crs='epsg:4326')

        if len(settlements_over_10km) > 0:

            settlements_over_10km.drop_duplicates(subset=['Longitud', 'Latitud'])
            path = os.path.join(folder_over, GID_id + '.shp')
            settlements_over_10km.to_file(path, crs='epsg:4326')

        path = os.path.join(folder_fiber, GID_id + '.shp')
        fiber.to_file(path, crs='epsg:4326')


def connect_main_settlement(iso3, level):
    """

    """
    folder = os.path.join(DATA_INTERMEDIATE, iso3)
    folder_out = os.path.join(folder, 'settlements', 'main_settlements')

    if not os.path.exists(folder_out):
        os.makedirs(folder_out)

    # folder_edges_intra = os.path.join(folder, 'network_routing_structure', 'intra')
    # if not os.path.exists(folder_edges_intra):
    #     os.makedirs(folder_edges_intra)

    folder_edges_inter = os.path.join(folder, 'network_routing_structure', 'inter')
    if not os.path.exists(folder_edges_inter):
        os.makedirs(folder_edges_inter)

    filename = 'regions_{}_{}.shp'.format(level, iso3)
    path = os.path.join(folder, 'regions', filename)
    regions = gpd.read_file(path, crs='epsg:4326')[:1]
    regions = regions.loc[regions.is_valid]

    for idx, region in tqdm(regions.iterrows(), total=regions.shape[0]):

        output = []

        GID_id = region["GID_{}".format(level)]

        path = os.path.join(folder, 'census_localidades', GID_id + '.shp')
        if not os.path.exists(path):
            continue
        localidades = gpd.read_file(path, crs='epsg:4326')

        path = os.path.join(folder_out, '..', GID_id + '.shp')
        if not os.path.exists(path):
            continue
        settlements = gpd.read_file(path, crs='epsg:4326')

        for idx, area in localidades.iterrows():
            for idx, settlement in settlements.iterrows():
                if settlement['geometry'].intersects(area['geometry']):
                    output.append({
                        'type': 'Feature',
                        'geometry': settlement['geometry'],
                        'properties': {
                            'GID_id': GID_id,
                            'census_localidades_id': area['FID'],
                            'population': settlement['Población'],
                            'distance': settlement['distance'],
                        }
                    })

        output = gpd.GeoDataFrame.from_features(output, crs='epsg:4326')
        path_nodes = os.path.join(folder_out, 'all_' + GID_id + '.shp')
        output.to_file(path_nodes, crs='epsg:4326')
        # path_edges = os.path.join(folder_edges_intra, GID_id + '.shp')
        # fit_edges(path_nodes, path_edges, GID_id)

        output = output.loc[output.reset_index().groupby([
            'census_localidades_id'])['population'].idxmax()]
        path_nodes = os.path.join(folder_out, 'main_' + GID_id + '.shp')
        output.to_file(path_nodes, crs='epsg:4326')

        path_edges = os.path.join(folder_edges_inter, GID_id + '.shp')
        fit_edges(path_nodes, path_edges, GID_id)

    return


def fit_edges(input_path, output_path, modeling_region):
    """
    Fit edges to nodes using a minimum spanning tree.

    Parameters
    ----------
    input_path : string
        Path to the node shapefiles.
    output_path : string
        Path for writing the network edge shapefiles.
    modeling_region : geojson
        The modeling region being assessed.

    """
    folder = os.path.dirname(output_path)
    if not os.path.exists(folder):
        os.makedirs(folder)

    nodes = gpd.read_file(input_path, crs='epsg:4326')
    nodes = nodes.to_crs('epsg:3857')

    all_possible_edges = []

    for node1_id, node1 in nodes.iterrows():
        for node2_id, node2 in nodes.iterrows():
            if node1_id != node2_id:
                geom1 = shape(node1['geometry'])
                geom2 = shape(node2['geometry'])
                line = LineString([geom1, geom2])
                all_possible_edges.append({
                    'type': 'Feature',
                    'geometry': mapping(line),
                    'properties':{
                        'from': node1_id,
                        'to':  node2_id,
                        'length': line.length,
                        'regions': modeling_region,
                    }
                })

    if len(all_possible_edges) == 0:
        return

    G = nx.Graph()

    for node_id, node in enumerate(nodes):
        G.add_node(node_id, object=node)

    for edge in all_possible_edges:
        G.add_edge(edge['properties']['from'], edge['properties']['to'],
            object=edge, weight=edge['properties']['length'])

    tree = nx.minimum_spanning_edges(G)

    edges = []

    for branch in tree:
        link = branch[2]['object']
        if link['properties']['length'] > 0:
            edges.append(link)

    edges = gpd.GeoDataFrame.from_features(edges, crs='epsg:3857')

    if len(edges) > 0:
        edges = edges.to_crs('epsg:4326')
        edges.to_file(output_path)

    return


def connect_intra_settlement(iso3, level):
    """

    """
    folder = os.path.join(DATA_INTERMEDIATE, iso3)
    folder_out = os.path.join(folder, 'settlements', 'intra_settlements', 'final')
    if not os.path.exists(folder_out):
        os.makedirs(folder_out)

    folder_edges_intra = os.path.join(folder, 'network_routing_structure', 'intra')
    if not os.path.exists(folder_edges_intra):
        os.makedirs(folder_edges_intra)

    filename = 'regions_{}_{}.shp'.format(level, iso3)
    path = os.path.join(folder, 'regions', filename)
    regions = gpd.read_file(path, crs='epsg:4326')[:5]
    regions = regions.loc[regions.is_valid]

    for idx, region in tqdm(regions.iterrows(), total=regions.shape[0]):

        GID_id = region["GID_{}".format(level)]

        path = os.path.join(folder, 'settlements', 'main_settlements', 'all_' + GID_id + '.shp')
        if not os.path.exists(path):
            continue
        settlements = gpd.read_file(path, crs='epsg:4326')

        unique_ids = settlements['census_loc'].unique()

        for unique_id in list(unique_ids):

            output = []

            for idx, settlement in settlements.iterrows():

                if unique_id == int(settlement['census_loc']):
                    output.append({
                        'type': 'Feature',
                        'geometry': settlement['geometry'],
                        'properties': {
                            'GID_id': settlement['GID_id'],
                            'census_loc': settlement['census_loc'],
                            'population': settlement['population'],
                            'distance': settlement['distance'],
                        }
                    })

            output = gpd.GeoDataFrame.from_features(output, crs='epsg:4326')
            # path_nodes = os.path.join(folder_out, 'all_' + GID_id + '.shp')
            # output.to_file(path_nodes, crs='epsg:4326')
            # path_edges = os.path.join(folder_edges_intra, GID_id + '.shp')
            # fit_edges(path_nodes, path_edges, GID_id)

            path_nodes = os.path.join(folder_out, GID_id + '_' + str(unique_id) + '.shp')
            output.to_file(path_nodes, crs='epsg:4326')

            path_edges = os.path.join(folder_edges_intra, GID_id + '_' + str(unique_id) + '.shp')
            fit_edges(path_nodes, path_edges, GID_id)

    return


def calculate_intra_distances(iso3, level):
    """

    """
    folder = os.path.join(DATA_INTERMEDIATE, iso3)
    folder_sets = os.path.join(folder, 'settlements', 'intra_settlements')
    folder_edges = os.path.join(folder, 'network_routing_structure', 'intra')

    filename = 'regions_{}_{}.shp'.format(level, iso3)
    path = os.path.join(folder, 'regions', filename)
    regions = gpd.read_file(path, crs='epsg:4326')#[:1]
    regions = regions.loc[regions.is_valid]

    for idx, region in tqdm(regions.iterrows(), total=regions.shape[0]):

        GID_id = region["GID_{}".format(level)]

        path = os.path.join(folder_sets, GID_id + '*.shp')
        set_files = glob(os.path.join(path))

        path = os.path.join(folder_edges, GID_id + '*.shp')
        edge_files = glob(os.path.join(path))

        for item in set_files:
            output = []
            basename1 = os.path.basename(item).split('_')[1][:-4]
            for edge in edge_files:
                basename2 = os.path.basename(edge).split('_')[1][:-4]
                if basename1 == basename2:
                    settlements = gpd.read_file(item, crs='epsg:4326')
                    edges = gpd.read_file(edge, crs='epsg:4326')
                    edges = edges.to_crs('epsg:3857')
                    edges['distance_m'] = edges['geometry'].length
                    sum_of_intra = edges['distance_m'].sum()
                    mean_of_intra = sum_of_intra / len(settlements)
                    for idx, settlement in settlements.iterrows():
                        output.append({
                            'type': 'Feature',
                            'geometry': settlement['geometry'],
                            'properties': {
                                'GID_id': settlement['GID_id'],
                                'census_loc': settlement['census_loc'],
                                'population': settlement['population'],
                                'mean_intra_length': mean_of_intra,
                                'distance': settlement['distance'],
                            }
                        })

            if len(output) == 0:
                continue

            output = gpd.GeoDataFrame.from_features(output, crs='epsg:4326')

            path_nodes = os.path.join(folder_sets, GID_id + str(basename1) + '.shp')
            output.to_file(path_nodes, crs='epsg:4326')



def calculate_inter_distances(iso3, level):
    """

    """
    folder = os.path.join(DATA_INTERMEDIATE, iso3)
    folder_sets = os.path.join(folder, 'settlements', 'main_settlements')
    folder_final = os.path.join(folder_sets, 'final')
    folder_edges = os.path.join(folder, 'network_routing_structure', 'inter')

    if not os.path.exists(folder_final):
        os.makedirs(folder_final)

    filename = 'regions_{}_{}.shp'.format(level, iso3)
    path = os.path.join(folder, 'regions', filename)
    regions = gpd.read_file(path, crs='epsg:4326')#[:1]
    regions = regions.loc[regions.is_valid]

    for idx, region in tqdm(regions.iterrows(), total=regions.shape[0]):

        GID_id = region["GID_{}".format(level)]

        path = os.path.join(folder_sets, 'main_' + GID_id + '.shp')
        if not os.path.exists(path):
            continue
        settlements = gpd.read_file(path, crs='epsg:4326')
        settlements = settlements.to_crs('epsg:3857')
        settlements['geometry'] = settlements['geometry'].buffer(100)

        path = os.path.join(folder_edges, GID_id + '.shp')
        if not os.path.exists(path):
            continue
        edges = gpd.read_file(path, crs='epsg:4326')
        edges = edges.to_crs('epsg:3857')

        output = []

        for idx, settlement in settlements.iterrows():
            sum_of_inter = 0
            number_of_inter = 0
            for idx, edge in edges.iterrows():
                if settlement['geometry'].intersects(edge['geometry']):
                    sum_of_inter += edge['geometry'].length
                    number_of_inter += 1

            if sum_of_inter == 0:
                mean_inter_length = 0
            else:
                mean_inter_length = sum_of_inter / number_of_inter

            output.append({
                'type': 'Feature',
                'geometry': settlement['geometry'].centroid,
                'properties': {
                    'GID_id': settlement['GID_id'],
                    'census_loc': settlement['census_loc'],
                    'population': settlement['population'],
                    'mean_inter_length': mean_inter_length,
                    'distance': settlement['distance'],
                }
            })

        if len(output) == 0:
            continue

        output = gpd.GeoDataFrame.from_features(output, crs='epsg:3857')
        output = output.to_crs('epsg:4326')

        path_nodes = os.path.join(folder_final, 'main_' + GID_id + '.shp')
        output.to_file(path_nodes, crs='epsg:4326')


def collect_settlements(iso3, level):
    """

    """
    folder = os.path.join(DATA_INTERMEDIATE, iso3)
    folder_intra = os.path.join(folder, 'settlements', 'intra_settlements', 'final')
    folder_inter = os.path.join(folder, 'settlements', 'main_settlements', 'final')
    folder_final = os.path.join(folder, 'settlements', 'final')

    if not os.path.exists(folder_final):
        os.makedirs(folder_final)

    filename = 'regions_{}_{}.shp'.format(level, iso3)
    path = os.path.join(folder, 'regions', filename)
    regions = gpd.read_file(path, crs='epsg:4326')[:20]
    regions = regions.loc[regions.is_valid]

    all_data = []

    for idx, region in tqdm(regions.iterrows(), total=regions.shape[0]):

        GID_id = region["GID_{}".format(level)]
        print(GID_id)
        #get inter settlement connections
        path = os.path.join(folder_inter, 'main_' + GID_id + '.shp')
        if not os.path.exists(path):
            continue
        main_settlements = gpd.read_file(path, crs='epsg:4326')

        path = os.path.join(folder_inter, '..', 'all_' + GID_id + '.shp')
        if not os.path.exists(path):
            continue
        all_settlements = gpd.read_file(path, crs='epsg:4326')

        output = []

        for idx, main_settlement in main_settlements.iterrows():
            for idx, all_settlement in all_settlements.iterrows():
                if str(main_settlement['census_loc']) == str(all_settlement['census_loc']):
                    all_data.append({
                        'x': all_settlement['geometry'].coords[0][0],
                        'y': all_settlement['geometry'].coords[0][1],
                        'GID_id': all_settlement['GID_id'],
                        'census_loc': all_settlement['census_loc'],
                        'population': all_settlement['population'],
                        'mean_intra_m': 0,
                        'mean_inter_dist_m': main_settlement['mean_inter'],
                        'distance': all_settlement['distance'],
                    })
                    output.append({
                        'type': 'Feature',
                        'geometry': all_settlement['geometry'],
                        'properties': {
                            'x': all_settlement['geometry'].coords[0][0],
                            'y': all_settlement['geometry'].coords[0][1],
                            'GID_id': all_settlement['GID_id'],
                            'census_loc': all_settlement['census_loc'],
                            'population': all_settlement['population'],
                            'mean_intra_m': 0,
                            'mean_inter_dist_m': main_settlement['mean_inter'],
                            'distance': all_settlement['distance'],
                        }
                    })

        if len(output) == 0:
            continue

        output = gpd.GeoDataFrame.from_features(output, crs='epsg:4326')

        output = output.drop_duplicates(subset=['geometry'])

        path_nodes = os.path.join(folder_final, GID_id + '.shp')
        output.to_file(path_nodes, crs='epsg:4326')

    all_data = pd.DataFrame(all_data)
    path_out = os.path.join(os.path.join(DATA_INTERMEDIATE, iso3, 'all_settlement_data.csv'))
    all_data.to_csv(path_out, index=False)





    #     #get intra settlement connections
    #     path = os.path.join(folder_intra, GID_id + '*.shp')
    #     set_files = glob(os.path.join(path))

    #     # output = []

    #     for idx, main_settlement in main_settlements.iterrows():

    #         for set_path in set_files:

    #             census_id = os.path.basename(set_path).split('_')[2][:-4]

    #             if int(main_settlement['census_loc']) == int(census_id):

    #                 settlements = gpd.read_file(set_path, crs='epsg:4326')
    #                 mean_inter_dist_m = main_settlement['mean_inter'] / len(settlements)

    #                 for idx, settlement in settlements.iterrows():

    #                     if 'mean_intra' in settlement:
    #                         mean_intra = settlement['mean_intra']
    #                     else:
    #                         mean_intra = 0

    #                 all_data.append({
    #                     'x': settlement['geometry'].coords[0][0],
    #                     'y': settlement['geometry'].coords[0][1],
    #                     'GID_id': settlement['GID_id'],
    #                     'census_loc': settlement['census_loc'],
    #                     'population': settlement['population'],
    #                     'mean_intra_m': mean_intra,
    #                     'mean_inter_dist_m': mean_inter_dist_m,
    #                     'distance': settlement['distance'],

    #             # 'type': 'Feature',
    #             # 'geometry': settlement['geometry'],
    #             # 'properties': {
    #                 # 'x': settlement['geometry'].coords[0][0],
    #                 # 'y': settlement['geometry'].coords[0][1],
    #                 # 'GID_id': settlement['GID_id'],
    #                 # 'census_loc': settlement['census_loc'],
    #                 # 'population': settlement['population'],
    #                 # 'mean_intra_m': mean_intra,
    #                 # 'mean_inter_dist_m': mean_inter_dist_m,
    #                 # 'distance': settlement['distance'],
    #             # }
    #         })

    #     # if len(output) == 0:
    #     #     continue

    #     # all_data = all_data + output

    #     # output = gpd.GeoDataFrame.from_features(output, crs='epsg:4326')

    #     # output = output.drop_duplicates(subset=['geometry'])

    #     # path_nodes = os.path.join(folder_final, GID_id + '.shp')
    #     # output.to_file(path_nodes, crs='epsg:4326')

    # all_data = pd.DataFrame(all_data)
    # path_out = os.path.join(os.path.join(DATA_INTERMEDIATE, iso3, 'all_settlement_data.csv'))
    # all_data.to_csv(path_out, index=False)


if __name__ == "__main__":

    iso3 = 'CHL'
    level = 3

    # ### Processing country boundary ready to export
    # process_country_shapes(iso3)

    # ### Processing regions ready to export
    # process_regions(iso3, level)

    # subset_road_network_by_region(iso3, level)

    # process_fiber()

    # chop_fiber_by_region(iso3, level)

    # filename = 'Entidades Censales Coberturas 2020-3.xlsx'
    # folder = os.path.join(DATA_RAW, 'Solicitud 9 de abril', '6')
    # path = os.path.join(folder, filename)

    # if not os.path.exists(path):
    #     load_original_data(path)

    # subset_census_entidades_by_region(iso3, level)

    # subset_localidades_points_by_region(iso3, level)

    # subset_localidades_polygons_by_region(iso3, level)

    # get_settlements_near_roads(iso3, level)

    # filter_settlements_far_from_roads(iso3, level)

    # connect_main_settlement(iso3, level)

    # connect_intra_settlement(iso3, level)

    # calculate_inter_distances(iso3, level)

    collect_settlements(iso3, level)

    # exclude ['Name_3'] == 'Ocean Islands'
