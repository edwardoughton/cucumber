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
from pathlib import Path
import json
import rasterio
from rasterio.mask import mask
from rasterstats import zonal_stats
import pyproj

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

    # if os.path.exists(os.path.join(path, 'national_outline.shp')):
    #     return 'Already completed national outline processing'

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

    single_country = single_country.to_crs('epsg:3857')

    geoms = []

    for idx, item in single_country.iterrows():
        for poly in item['geometry']:
            if poly.representative_point().coords[0][0] > -8500000:
            # if poly.area > 200000000: #(200 km^2)
                geoms.append({
                    'type': 'Polygon',
                    'geometry': poly,
                    'properties': {}
                })

    single_country = gpd.GeoDataFrame.from_features(geoms, crs='epsg:3857')
    single_country = single_country.to_crs('epsg:4326')

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

        if regional_level == 2:
            regions = regions.drop(regions[regions['GID_2'] == 'CHL.16.1_1'].index)
        if regional_level == 3:
            regions = regions.drop(regions[regions['GID_3'] == 'CHL.16.1.1_1'].index)

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


def load_entidades_data():
    """

    """
    filename = 'Entidades Censales Coberturas 2020-3.shp'
    folder = os.path.join(DATA_INTERMEDIATE, 'CHL', 'census_units')
    path_out = os.path.join(folder, filename)

    if os.path.exists(path_out):
        return

    print('--Working on census entidades')

    if not os.path.exists(folder):
        os.makedirs(folder)

    filename = 'Entidades Censales Coberturas 2020-3.xlsx'
    folder = os.path.join(DATA_RAW, 'Solicitud 9 de abril', '6')
    path = os.path.join(folder, filename)

    df = pd.read_excel (path, sheet_name='Entidades Censo')#[:10]
    df = df[['Longitud', 'Latitud', 'Region', 'Comuna', 'Población']] #'Localidad',
    df.columns = ['Longitud', 'Latitud', 'REGION', 'COMUNA', 'PERSONAS']

    data = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(
        df.Longitud, df.Latitud))

    data.to_file(path_out, crs='epsg:4326')


def load_metropolitana_data():
    """

    """
    filenames = [
        ('Manzana_Variables_C17_Region_Metropolitana-4.xls',
            'Manzana_Variables_C17_Region_Me'),
        ('Manzana_Variables_C17_Resto_del_Pais_Norte-2.xls',
            'Manzana_Variables_C17_Resto_del'),
        ('Manzana_Variables_C17_Resto_del_Pais_Sur-2.xls',
            'Manzana_Variables_C17_Resto_del'),
        ]

    for filename_input in filenames:

        filename_output = filename_input[0][:-4]
        folder = os.path.join(DATA_INTERMEDIATE, 'CHL', 'census_units')
        path_out = os.path.join(folder, filename_output + '.shp')

        if os.path.exists(path_out):
            continue

        print('--Working on census metripolitana {}'.format(filename_input[0]))

        if not os.path.exists(folder):
            os.makedirs(folder)

        folder = os.path.join(DATA_RAW, 'Solicitud 9 de abril', '6')
        path = os.path.join(folder, filename_input[0])

        df = pd.read_excel (path, sheet_name=filename_input[1])
        df = df[['Longitud', 'Latitud', 'REGION', 'COMUNA', 'PERSONAS']]

        data = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(
            df.Longitud, df.Latitud))

        data.to_file(path_out, crs='epsg:4326')


def combine_census_data():
    """
    Combine together urban and rural units.

    """
    filename = 'all_census_units.shp'
    folder = os.path.join(DATA_INTERMEDIATE, 'CHL', 'census_units')
    path_out = os.path.join(folder, filename)

    if os.path.exists(path_out):
        return

    print('--Working on combining all census units')

    inclusions = [
        ('Entidades Censales Coberturas 2020-3', 'rural'),
        ('Manzana_Variables_C17_Region_Metropolitana-4', 'urban'),
        ('Manzana_Variables_C17_Resto_del_Pais_Norte-2', 'urban'),
        ('Manzana_Variables_C17_Resto_del_Pais_Sur-2', 'urban'),
    ]

    output = []
    pop = 0
    for path in Path(folder).rglob('*'):
        for item in inclusions:
            basename = os.path.basename(path)[:-4]
            if basename == item[0]:
                if os.path.basename(path).endswith('.shp'):

                    data = gpd.read_file(path, crs='epsg:4326')
                    data['type'] = item[1]
                    data = data.to_dict('records')
                    for datum in data:
                        output.append({
                            'type': 'Feature',
                            'geometry': datum['geometry'],
                            'properties': {
                                'REGION': datum['REGION'],
                                'COMUNA': datum['COMUNA'],
                                'PERSONAS': datum['PERSONAS'],
                                'type': datum['type'],
                            }
                        })
                        if not datum['PERSONAS'] == 'Sin Dato':
                            pop += int(datum['PERSONAS'])

    output = gpd.GeoDataFrame.from_features(output, crs='epsg:4326')

    output.to_file(path_out, crs='epsg:4326')


def subset_census_units_by_region(iso3, level):
    """
    Write out census units by region.

    """
    filename = 'all_census_units.shp'
    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'census_units')
    path = os.path.join(folder, filename)
    census_entities = gpd.read_file(path, crs='epsg:4326')

    filename = 'regions_{}_{}.shp'.format(level, iso3)
    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'regions')
    path = os.path.join(folder, filename)
    regions = gpd.read_file(path, crs='epsg:4326')#[:1]
    regions = regions.loc[regions.is_valid]

    out_folder = os.path.join(DATA_INTERMEDIATE, iso3, 'census_units', 'by_region')
    if not os.path.exists(out_folder):
        os.makedirs(out_folder)

    for idx, region in tqdm(regions.iterrows(), total=regions.shape[0]):

        GID_id = region["GID_{}".format(level)]

        path = os.path.join(out_folder, GID_id + '.shp')

        if os.path.exists(path):
            continue

        geo_region = gpd.GeoDataFrame(geometry=gpd.GeoSeries(region['geometry']),
            crs='epsg:4326')

        settlements = gpd.overlay(census_entities, geo_region, how='intersection')

        if len(settlements) > 0:

            settlements.to_file(path, crs='epsg:4326')

    print('Completed subsetting of census entidades')


def process_night_lights(iso3, level):
    """
    Clip the nightlights layer to the chosen country boundary and place in
    desired country folder.

    Parameters
    ----------
    country : string
        Three digit ISO country code.

    """
    folder = os.path.join(DATA_INTERMEDIATE, iso3)
    path_output = os.path.join(folder,'night_lights.tif')

    if os.path.exists(path_output):
        return print('Completed processing of nightlight layer')

    path_country = os.path.join(folder, 'national_outline.shp')

    filename = 'F182013.v4c_web.stable_lights.avg_vis.tif'
    path_night_lights = os.path.join(DATA_RAW, 'nightlights', '2013',
        filename)

    country = gpd.read_file(path_country, crs='epsg:4326')

    print('----')
    print('working on {}'.format(iso3))

    bbox = country.envelope

    geo = gpd.GeoDataFrame()
    geo = gpd.GeoDataFrame({'geometry': bbox}, crs='epsg:4326')

    coords = [json.loads(geo.to_json())['features'][0]['geometry']]

    night_lights = rasterio.open(path_night_lights, "r+")
    night_lights.nodata = 0

    out_img, out_transform = mask(night_lights, coords, crop=True)

    out_meta = night_lights.meta.copy()

    out_meta.update({"driver": "GTiff",
                    "height": out_img.shape[1],
                    "width": out_img.shape[2],
                    "transform": out_transform,
                    "crs": 'epsg:4326'})

    with rasterio.open(path_output, "w", **out_meta) as dest:
            dest.write(out_img)

    return print('Completed processing of night lights layer')


def process_settlement_layer(iso3, regional_level):
    """
    Clip the settlement layer to the chosen country boundary
    and place in desired country folder.

    Parameters
    ----------
    country : dict
        Contains all desired country information.

    """
    path_settlements = os.path.join(DATA_RAW,'settlement_layer',
        'ppp_2020_1km_Aggregated.tif')

    settlements = rasterio.open(path_settlements, 'r+')
    settlements.nodata = 255
    settlements.crs = {"init": "epsg:4326"}

    path_country = os.path.join(DATA_INTERMEDIATE, iso3,
        'national_outline.shp')

    if os.path.exists(path_country):
        country = gpd.read_file(path_country)
    else:
        print('Must generate national_outline.shp first' )

    path_country = os.path.join(DATA_INTERMEDIATE, iso3)
    shape_path = os.path.join(path_country, 'settlements.tif')

    if os.path.exists(shape_path):
        return print('Completed settlement layer processing')

    print('----')
    print('Working on {} level {}'.format(iso3, regional_level))

    bbox = country.envelope
    geo = gpd.GeoDataFrame()

    geo = gpd.GeoDataFrame({'geometry': bbox})

    coords = [json.loads(geo.to_json())['features'][0]['geometry']]

    out_img, out_transform = mask(settlements, coords, crop=True)

    out_meta = settlements.meta.copy()

    out_meta.update({"driver": "GTiff",
                    "height": out_img.shape[1],
                    "width": out_img.shape[2],
                    "transform": out_transform,
                    "crs": 'epsg:4326'})

    with rasterio.open(shape_path, "w", **out_meta) as dest:
            dest.write(out_img)

    return print('Completed processing of settlement layer')


def process_age_sex_structure(country):
    """
    Clip each demographic layer to the chosen country boundary
    and place in desired country folder.

    Parameters
    ----------
    country : dict
        Contains all desired country information.

    """
    path = os.path.join(DATA_RAW, 'settlement_layer')
    all_paths = glob.glob(path + '/*.tif')

    for path in all_paths:

        # if os.path.basename(path).startswith('ppp_2020_1km_Aggregated'):
        #     continue

        directory_out = os.path.join(DATA_INTERMEDIATE, iso3, 'age_sex_structure')

        if not os.path.exists(directory_out):
            os.makedirs(directory_out)

        filename = os.path.basename(path)
        path_out = os.path.join(directory_out, filename)

        if os.path.exists(path_out):
            continue

        settlements = rasterio.open(path, 'r+')
        settlements.nodata = 0
        settlements.crs = {"init": "epsg:4326"}

        filename = 'national_outline.shp'
        path_country = os.path.join(DATA_INTERMEDIATE, iso3, filename)

        if os.path.exists(path_country):
            country = gpd.read_file(path_country)
        else:
            print('Must generate national_outline.shp first' )

        geo = gpd.GeoDataFrame({'geometry': country['geometry']})

        coords = [json.loads(geo.to_json())['features'][0]['geometry']]

        #chop on coords
        out_img, out_transform = mask(settlements, coords, crop=True)

        # Copy the metadata
        out_meta = settlements.meta.copy()

        out_meta.update({"driver": "GTiff",
                        "height": out_img.shape[1],
                        "width": out_img.shape[2],
                        "transform": out_transform,
                        "crs": 'epsg:4326'})

        with rasterio.open(path_out, "w", **out_meta) as dest:
                dest.write(out_img)

    return print('Completed processing of settlement layer')


def get_regional_data(iso3, level):
    """
    Extract regional data including luminosity and population.

    Parameters
    ----------
    country : dict
        Contains all desired country information.

    """
    gid_level = 'GID_{}'.format(level)

    filename = 'regional_data.csv'
    path_output = os.path.join(DATA_INTERMEDIATE, iso3, filename)

    # if os.path.exists(path_output):
    #     return print('Regional data already exists')

    path_country = os.path.join(DATA_INTERMEDIATE, iso3,
        'national_outline.shp')

    single_country = gpd.read_file(path_country)

    path_settlements = os.path.join(DATA_INTERMEDIATE, iso3,
        'settlements.tif')

    path_night_lights = os.path.join(DATA_INTERMEDIATE, iso3,
        'night_lights.tif')

    filename = 'regions_{}_{}.shp'.format(level, iso3)
    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'regions')
    path = os.path.join(folder, filename)
    regions = gpd.read_file(path)#[:1]

    results = []

    for index, region in regions.iterrows():

        with rasterio.open(path_settlements) as src:

            affine = src.transform
            array = src.read(1)
            array[array <= 0] = 0

            pop_summation = [d['sum'] for d in zonal_stats(
                region['geometry'],
                array,
                stats=['sum'],
                nodata=0,
                affine=affine)][0]

        with rasterio.open(path_night_lights) as src:

            affine = src.transform
            array = src.read(1)
            array[array <= 0] = 0

            luminosity_summation = [d['sum'] for d in zonal_stats(
                region['geometry'],
                array,
                stats=['sum'],
                nodata=0,
                affine=affine)][0]

        area_km2 = round(area_of_polygon(region['geometry']) / 1e6)

        if luminosity_summation == None:
            luminosity_summation = 0

        if area_km2 == 0:
            continue

        results.append({
            'GID_0': region['GID_0'],
            'GID_id': region[gid_level],
            'GID_level': gid_level,
            'population_total': pop_summation,
            # 'population_over_10': (pop['population_f_over_10'] +
            #     pop['population_m_over_10']),
            # 'population_f_over_10': pop['population_f_over_10'],
            # 'population_m_over_10': pop['population_m_over_10'],
            'area_km2': area_km2,
            'population_km2': (pop_summation /
                area_km2 if pop_summation else 0),
            # 'population_over_10yrs_km2': (
            #     (pop['population_f_over_10'] + pop['population_m_over_10']) /
            #     area_km2 if pop_summation else 0),
            'mean_luminosity_km2': (luminosity_summation /
                area_km2 if luminosity_summation else 0)
        })

    results_df = pd.DataFrame(results)

    results_df.to_csv(path_output, index=False)

    print('Completed {}'.format(single_country.NAME_0.values[0]))

    return print('Completed night lights data querying')


def area_of_polygon(geom):
    """
    Returns the area of a polygon. Assume WGS84 as crs.

    """
    geod = pyproj.Geod(ellps="WGS84")

    poly_area, poly_perimeter = geod.geometry_area_perimeter(
        geom
    )

    return abs(poly_area)


def forecast_subscriptions(country):
    """
    Forecast the number of unique cellular subscriptions.

    Parameters
    ----------
    country : dict
        Contains all country specfic information.

    """
    path = os.path.join(DATA_RAW, 'gsma', 'gsma_unique_subscribers.csv')
    historical_data = load_subscription_data(path, country['iso3'])

    start_point = 2021
    end_point = 2030
    horizon = 4

    forecast = forecast_linear(
        country,
        historical_data,
        start_point,
        end_point,
        horizon
    )

    forecast_df = pd.DataFrame(historical_data + forecast)

    path = os.path.join(DATA_INTERMEDIATE, iso3, 'subscriptions')

    if not os.path.exists(path):
        os.mkdir(path)

    forecast_df.to_csv(os.path.join(path, 'subs_forecast.csv'), index=False)

    path = os.path.join(BASE_PATH, '..', 'vis', 'subscriptions', 'data_inputs')
    if not os.path.exists(path):
        os.makedirs(path)
    forecast_df.to_csv(os.path.join(path, '{}.csv'.format(iso3)), index=False)

    return print('Completed subscription forecast')


def load_subscription_data(path, iso3):
    """
    Load in itu cell phone subscription data.

    Parameters
    ----------
    path : string
        Location of itu data as .csv.
    iso3 : string
        ISO3 digital country code.

    Returns
    -------
    output : list of dicts
        Time series data of cell phone subscriptions.

    """
    output = []

    historical_data = pd.read_csv(path, encoding = "ISO-8859-1")
    historical_data = historical_data.to_dict('records')

    # genders = ['female', 'male']
    scenarios = ['low', 'baseline', 'high']

    # for gender in genders:
    for scenario in scenarios:
        for year in range(2010, 2021):
            year = str(year)
            for item in historical_data:
                if item['iso3'] == iso3:

                    # adjusted_penetration = adjust_penetration(country,
                    #     gender, float(item[year]) * 100)

                    output.append({
                        'scenario': scenario,
                        'country': iso3,
                        # 'gender': gender,
                        'penetration': float(item[year] * 100),
                        'year':  year,
                    })

    return output


def forecast_linear(country, historical_data, start_point, end_point, horizon):
    """
    Forcasts subscription adoption rate.

    Parameters
    ----------
    historical_data : list of dicts
        Past penetration data.
    start_point : int
        Starting year of forecast period.
    end_point : int
        Final year of forecast period.
    horizon : int
        Number of years to use to estimate mean growth rate.

    Returns
    -------
    output : list of dicts
        Time series data of cell phone subscriptions.

    """
    output = []

    # genders = ['female', 'male']
    scenarios = ['low', 'baseline', 'high']

    # for gender in genders:

        # by_gender = [d for d in historical_data if d['gender'] == gender]

    for scenario in scenarios:

        scenario_data = []

        subs_growth = country['subs_growth_{}'.format(scenario)]

        year_0 = sorted(historical_data, key = lambda i: i['year'], reverse=True)[0]

        for year in range(start_point, end_point + 1):

            if year == start_point:

                penetration = year_0['penetration'] * (1 + (subs_growth/100))

                # penetration = adjust_penetration(country, gender, penetration)

            else:
                penetration = penetration * (1 + (subs_growth/100))

            if year not in [item['year'] for item in scenario_data]:

                scenario_data.append({
                    'scenario': scenario,
                    'country': country['iso3'],
                    # 'gender': gender,
                    'year': year,
                    'penetration': round(penetration, 2),
                })

        output = output + scenario_data

    return output


def adjust_penetration(country, gender, penetration):
    """
    Adjust penetration.

    """
    female_gender_diff = (country['phone_ownership_male'] -
        country['phone_ownership_female'])

    if gender == 'female' and female_gender_diff >= 0:
        return penetration - (female_gender_diff / 2)
    elif gender == 'female' and female_gender_diff < 0:
        return penetration + (female_gender_diff / 2)
    elif gender == 'male' and female_gender_diff >= 0:
        return penetration + (female_gender_diff / 2)
    elif gender == 'male' and female_gender_diff < 0:
        return penetration - (female_gender_diff / 2)
    else:
        print('Did not recognize female gender difference parameter')


def forecast_smartphones(country, level):
    """
    Forecast smartphone adoption.

    Parameters
    ----------
    country : dict
        Contains all country specfic information.

    """
    filename = 'wb_smartphone_survey.csv'
    path = os.path.join(DATA_RAW, 'wb_smartphone_survey', filename)
    survey_data = load_smartphone_data(path, iso3)

    start_point = 2020
    end_point = 2030

    forecast = forecast_smartphones_linear(
        survey_data,
        country,
        start_point,
        end_point
    )

    forecast_df = pd.DataFrame(forecast)

    path = os.path.join(DATA_INTERMEDIATE, iso3, 'subscriptions')

    if not os.path.exists(path):
        os.mkdir(path)

    forecast_df.to_csv(os.path.join(path, 'smartphone_forecast.csv'), index=False)

    path = os.path.join(BASE_PATH, '..', 'vis', 'smartphones', 'data_inputs')
    if not os.path.exists(path):
        os.makedirs(path)
    forecast_df.to_csv(os.path.join(path, '{}.csv'.format(iso3)), index=False)

    return print('Completed subscription forecast')


def load_smartphone_data(path, iso3):
    """
    Load smartphone adoption survey data.

    Parameters
    ----------
    path : string
        Location of data as .csv.
    country : string
        ISO3 digital country code.

    """
    survey_data = pd.read_csv(path)

    survey_data = survey_data.to_dict('records')

    countries_with_data = [i['iso3'] for i in survey_data]

    output = []

    if iso3 in countries_with_data:
        for item in survey_data:
                if item['iso3'] == iso3:
                    output.append({
                        'country': item['iso3'],
                        'cluster': item['cluster'],
                        'settlement_type': item['Settlement'],
                        'smartphone_penetration': item['Smartphone']
                    })

    else:
        for item in survey_data:
            if item['cluster'] == country['cluster']:
                output.append({
                    'country': country['iso3'],
                    'cluster': item['cluster'],
                    'settlement_type': item['Settlement'],
                    'smartphone_penetration': item['Smartphone']
                })

    return output


def forecast_smartphones_linear(data, country, start_point, end_point):
    """
    Forecast smartphone adoption.

    Parameters
    ----------
    data : list of dicts
        Survey data.
    country : string
        ISO3 digital country code.
    start_point : int
        Starting year of forecast period.
    end_point : int
        Final year of forecast period.

    Returns
    -------
    output : list of dicts
        Time series forecast of smartphone penetration.

    """
    output = []

    scenarios = ['low', 'baseline', 'high']
    settlement_types = ['urban', 'rural']

    for scenario in scenarios:
        for settlement_type in settlement_types:

            smartphone_growth = country['sp_growth_{}_{}'.format(scenario, settlement_type)]

            for item in data:

                if not item['settlement_type'].lower() == settlement_type:

                    continue

                for year in range(start_point, end_point + 1):

                    if year == start_point:

                        penetration = item['smartphone_penetration']

                    else:

                        penetration = penetration * (1 + (smartphone_growth/100))

                    if penetration > 95:
                        penetration = 95

                    output.append({
                        'scenario': scenario,
                        'country': item['country'],
                        'settlement_type': item['settlement_type'].lower(),
                        'year': year,
                        'penetration': round(penetration, 2),
                    })

    return output

if __name__ == "__main__":

    iso3 = 'CHL'
    level = 3

    process_country_shapes(iso3)

    process_regions(iso3, level)

    load_entidades_data()

    load_metropolitana_data()

    combine_census_data()

    subset_census_units_by_region(iso3, level)

    process_night_lights(iso3, level)

    process_settlement_layer(iso3, level)

    get_regional_data(iso3, level)

    forecast_subscriptions(country)

    forecast_smartphones(country, level)
