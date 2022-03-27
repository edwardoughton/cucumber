"""
Read in available site data

Written by Ed Oughton

21st April 2020

"""
import os
import csv
import configparser
import pandas as pd
import geopandas as gpd
import xlrd
import numpy as np
from shapely.geometry import MultiPolygon
from shapely.ops import transform, unary_union
import rasterio
# from rasterio.mask import mask
from rasterstats import zonal_stats
import pyproj
import random

from countries import COUNTRY_LIST

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw', 'real_site_data')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')


def process_unconstrained_site_estimation(country):
    """
    Allocate towers using an unconstrained site estimation process.

    """
    iso3 = country['iso3']

    filename = 'regional_data.csv'
    path = os.path.join(DATA_INTERMEDIATE, iso3, filename)
    regional_data = pd.read_csv(path)

    path = os.path.join(DATA_INTERMEDIATE, iso3, 'coverage', 'coverage.csv')
    coverage_data = pd.read_csv(path)

    coverage_lut = {}

    for idx, region in coverage_data.iterrows():
        techs = ['2G', '3G', '4G']
        for tech in techs:
            if region['generation'] == tech:
                coverage_lut[region['GID_id']] = {
                    tech: region['coverage_km2'],
                }

    filename = 'wb_population_coverage_3G.csv'
    path = os.path.join(DATA_RAW, '..', 'wb_mobile_coverage', filename)
    coverage = pd.read_csv(path, encoding = "ISO-8859-1")
    coverage = coverage.loc[coverage['Country ISO3'] == iso3]
    coverage = coverage['2020'].values[0]

    population = regional_data['population'].sum()
    population_covered = population * (coverage / 100)

    path = os.path.join(DATA_RAW, 'tower_counts', 'tower_counts.csv')
    towers = pd.read_csv(path, encoding = "ISO-8859-1")
    towers = towers.loc[towers['ISO_3digit'] == iso3]
    towers = towers['count'].values[0]
    towers_per_pop = towers / population_covered

    backhaul_lut = get_backhaul_lut(iso3, country['region'], '2025')

    regional_data = regional_data.to_dict('records')
    data = sorted(regional_data, key=lambda k: k['population_km2'], reverse=True)

    output = []

    covered_pop_so_far = 0

    for region in data:

        if covered_pop_so_far < population_covered:
            sites_estimated_total = region['population'] * towers_per_pop
            sites_estimated_km2 = region['population_km2'] * towers_per_pop

        else:
            sites_estimated_total = 0
            sites_estimated_km2 = 0

        backhaul_estimates = estimate_backhaul(sites_estimated_total, backhaul_lut)

        if region['GID_id'] in coverage_lut:
            region_coverage = coverage_lut[region['GID_id']]
            if '4G' in region_coverage:
                sites_4G = (region_coverage['4G'] / 100)
            else:
                sites_4G = 0
        else:
            sites_4G = 0

        output.append({
            'GID_0': region['GID_0'],
            region['GID_level']: region['GID_id'],
            'population': region['population'],
            'area_km2': region['area_km2'],
            # 'sites_2G': int(coverage_lut[region['GID_id']['2G']] * sites_estimated_total),
            # 'sites_3G': int(coverage_lut[region['GID_id']]['3G'] * sites_estimated_total),
            'sites_4G': int(sites_4G * sites_estimated_total) if sites_4G else 0,
            'total_estimated_sites': round(sites_estimated_total),
            'sites_estimated_km2': sites_estimated_km2,
            'backhaul_fiber': backhaul_estimates['backhaul_fiber'],
            'backhaul_copper': backhaul_estimates['backhaul_copper'],
            'backhaul_wireless': backhaul_estimates['backhaul_wireless'],
            'backhaul_satellite': backhaul_estimates['backhaul_satellite'],
        })

        if region['population'] == None:
            continue

        covered_pop_so_far += region['population']

    output = pd.DataFrame(output)
    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'sites')
    if not os.path.exists(folder):
        os.makedirs(folder)
    path = os.path.join(folder, 'sites.csv')
    output.to_csv(path, index=False)

    return output


def process_costa_rica(country, technologies):

    iso3 = country['iso3']

    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'sites')
    if not os.path.exists(folder):
        os.makedirs(folder)

    filename = 'regions_2_{}.shp'.format(iso3)
    path = os.path.join(DATA_INTERMEDIATE, iso3, 'regions', filename)
    regions = gpd.read_file(path, crs='epsg:4326')#[:2]

    path = os.path.join(DATA_RAW, iso3, 'RadioBases móviles I Semestre 2020.xlsx')

    df = pd.read_excel(path, 'Datos', skiprows=6)

    df = df[['Code of antenna/ base station',
        'GIS coordinates: Longitude (*)', 'GIS coordinates: Latitude (*)',
        'Band in use (*)',
        'Antenna model/ technology (GSM, LTE, etc.) (*)',
    ]]
    df.columns = ['site_id', 'longitude', 'latitude', 'spectrum',
        'technology', #'backhaul', 'on_grid'
        ]
    df = df.dropna()

    df = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.longitude, df.latitude))

    df = df.drop_duplicates(['site_id'])

    interim = []

    for idx, point in df.iterrows():
        for idx, region in regions.iterrows():
            if point['geometry'].intersects(region['geometry']):
                interim.append({
                    'type': 'Feature',
                    'geometry': point['geometry'],
                    'properties': {
                        'site_id': point['site_id'],
                        # 'site_name': point['site_name'],
                        'technology': point['technology'],
                        'spectrum': point['spectrum'],
                        # 'backhaul': point['backhaul'],
                        # 'on_grid': point['on_grid'],
                        'GID_2': region['GID_2'],
                    }
                })

    df = gpd.GeoDataFrame().from_features(interim, crs='epsg:4326')

    filename = 'sites.shp'
    df.to_file(os.path.join(folder, filename), crs='epsg:4326')

    backhaul_lut = get_backhaul_lut(iso3, country['region'], '2025')

    output = []

    for idx, region in regions.iterrows():

        sites_2G = 0
        sites_3G = 0
        sites_4G = 0
        # wireless = 0
        # fiber = 0
        # on_grid = 0
        # off_grid = 0

        for idx, point in df.iterrows():
            if region['geometry'].intersects(point['geometry']):

                techs = []

                if '2G' in point['technology']:
                    techs.append('2G')
                if '3G' in point['technology']:
                    techs.append('3G')
                if '4G' in point['technology']:
                    techs.append('4G')

                if '4G' in techs:
                    sites_4G += 1
                elif '3G' in techs:
                    sites_3G += 1
                elif '2G' in techs:
                    sites_2G += 1
                else:
                    print('Did not reconize any technologies')

        total_sites = sites_2G + sites_3G + sites_4G
        backhaul_estimates = estimate_backhaul(total_sites, backhaul_lut)

        output.append({
            'GID_0': region['GID_0'],
            'GID_2': region['GID_2'],
            'sites_2G': sites_2G,
            'sites_3G': sites_3G,
            'sites_4G': sites_4G,
            'total_estimated_sites': sites_2G + sites_3G + sites_4G,
            'backhaul_fiber': backhaul_estimates['backhaul_fiber'],
            'backhaul_copper': backhaul_estimates['backhaul_copper'],
            'backhaul_wireless': backhaul_estimates['backhaul_wireless'],
            'backhaul_satellite': backhaul_estimates['backhaul_satellite'],
        })

    output = pd.DataFrame(output)
    output.to_csv(os.path.join(folder, 'sites.csv'), index=False)


def process_the_gambia():

    folder = os.path.join(DATA_INTERMEDIATE, 'GMB', 'sites')
    if not os.path.exists(folder):
        os.makedirs(folder)

    path = os.path.join(DATA_INTERMEDIATE, 'GMB', 'regions', 'regions_2_GMB.shp')
    regions = gpd.read_file(path, crs='epsg:4326')

    path = os.path.join(DATA_RAW, 'GMB', 'Gambia Network_Africell.xlsx')
    process_all_sites_the_gambia(path, regions, folder)

    sites_lut = sites_lut_the_gambia(path, regions, folder)

    print('Writing The Gambia csv data')
    sites_lut.to_csv(os.path.join(folder, 'sites.csv'), index=False)


def process_all_sites_the_gambia(path, regions, folder):

    df = pd.read_excel(path, 'Sites', skiprows=1)

    df = df[['Site_ID', 'site_name', 'Longitude', 'Latitude',
        '2G, 3G, 4G, Wifi etc', #technology?
        'Fibre, microwave', #backhaul type?
        'Yes / No', #main grid?
    ]]
    df.columns = ['site_id', 'site_name', 'longitude', 'latitude',
        'technology', 'backhaul', 'on_grid']
    df = df.dropna()

    df = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.longitude, df.latitude))

    df = df.drop_duplicates(['site_id'])

    output = []

    for idx, point in df.iterrows():
        for idx, region in regions.iterrows():
            if point['geometry'].intersects(region['geometry']):
                output.append({
                    'type': 'Feature',
                    'geometry': point['geometry'],
                    'properties': {
                        'site_id': point['site_id'],
                        'site_name': point['site_name'],
                        'technology': point['technology'],
                        'backhaul': point['backhaul'],
                        'on_grid': point['on_grid'],
                        'GID_2': region['GID_2'],
                    }
                })

    df = gpd.GeoDataFrame().from_features(output, crs='epsg:4326')

    filename = 'sites.shp'
    df.to_file(os.path.join(folder, filename), crs='epsg:4326')

    return df


def sites_lut_the_gambia(path, regions, folder):
    """

    """
    df = pd.read_excel(path, 'Sites', skiprows=1)

    df = df[['Site_ID', 'site_name', 'Longitude', 'Latitude',
        '2G, 3G, 4G, Wifi etc', #technology?
        'Fibre, microwave', #backhaul type?
        'Yes / No', #main grid?
    ]]
    df.columns = ['site_id', 'site_name', 'longitude', 'latitude',
        'technology', 'backhaul', 'on_grid']
    df = df.dropna()

    df = gpd.GeoDataFrame(
        df, geometry=gpd.points_from_xy(df.longitude, df.latitude))

    df = df.drop_duplicates(['site_id'])

    output = []

    for idx, region in regions.iterrows():

        sites_2G = 0
        sites_3G = 0
        sites_4G = 0
        wireless = 0
        fiber = 0
        on_grid = 0
        off_grid = 0

        for idx, point in df.iterrows():
            if region['geometry'].intersects(point['geometry']):

                if '2G' in point['technology']:
                    sites_2G += 1
                if '3G' in point['technology']:
                    sites_3G += 1
                if '4G' in point['technology']:
                    sites_4G += 1
                if 'Microwave' in point['backhaul']:
                    wireless += 1
                if 'Fibre' in point['backhaul']:
                    fiber += 1
                if 'Yes' in point['on_grid']:
                    on_grid += 1
                if 'No' in point['on_grid']:
                    off_grid += 1

        output.append({
            # 'type': 'Feature',
            # 'geometry': region['geometry'],
            # 'properties': {
            'GID_0': region['GID_0'],
            'GID_2': region['GID_2'],
            'sites_2G': sites_2G,
            'sites_3G': sites_3G,
            'sites_4G': sites_4G,
            'total_estimated_sites': sites_2G + sites_3G + sites_4G,
            'backhaul_wireless': wireless,
            'backhaul_fiber':  fiber / (wireless + fiber) * 100 if fiber else 0,
            'on_grid': on_grid ,
            'off_grid': off_grid,
        })

    output = pd.DataFrame(output)

    return output


def process_senegal(country, technologies):
    """
    Process site data for Senegal.

    """
    level = country['regional_level']
    iso3 = country['iso3']
    gid_level = 'GID_{}'.format(level)

    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'sites')
    if not os.path.exists(folder):
        os.makedirs(folder)

    filename = 'regions_{}_{}.shp'.format(country['regional_level'], iso3)
    path = os.path.join(DATA_INTERMEDIATE, iso3, 'regions', filename)
    regions = gpd.read_file(path, crs='epsg:4326')#[:1]

    path_settlements = os.path.join(DATA_INTERMEDIATE, iso3, 'settlements.tif')

    filename = 'Bilan_Couverture_Orange_Dec2017.csv'
    path = os.path.join(DATA_RAW, 'SEN', filename)

    sites = pd.read_csv(path, encoding = "ISO-8859-1")
    sites = sites[['Cell_ID', 'Site_Name', 'LATITUDE', 'LONGITUDE']].reset_index()
    sites = gpd.GeoDataFrame(
        sites, geometry=gpd.points_from_xy(sites.LONGITUDE, sites.LATITUDE),
        crs='epsg:31028')
    sites = sites.dropna()
    sites = sites.to_crs('epsg:4326')

    lut = {}

    for tech in technologies:

        folder = os.path.join(DATA_INTERMEDIATE, iso3, 'coverage')
        path =  os.path.join(folder, 'coverage_{}.shp'.format(tech))

        if not os.path.exists(path):
            coverage = 0
        else:
            coverage = gpd.read_file(path, crs='epsg:4326')

        region_lut = {}

        for idx, region in regions.iterrows():

            if not os.path.exists(path):
                region_lut[region[gid_level]] = 0
                print('Coverage path did not exist')
                continue

            if region['geometry'].geom_type == 'Polygon':
                polygons = []
                polygons.append(region['geometry'])
            if region['geometry'].geom_type == 'MultiPolygon':
                polygons = list(region['geometry'])

            geo = gpd.GeoDataFrame.from_features(
                [
                    {'geometry': poly, 'properties': {}}
                    for poly in polygons
                ],
                crs='epsg:4326'
            )

            region_coverage = gpd.overlay(geo, coverage, how='intersection')

            if len(region_coverage) == 0:
                region_lut[region[gid_level]] = 0
                print('No regional coverage for {} in {}'.format(tech, region[gid_level]))
                continue

            region_sites = gpd.overlay(sites, region_coverage, how='intersection')

            if len(sites) == 0:
                region_lut[region[gid_level]] = 0
                print('No sites for {} in {}'.format(tech, region[gid_level]))
                continue

            region_lut[region[gid_level]] = len(region_sites)

        interim = {}
        interim[tech] = region_lut
        lut.update(interim)

    backhaul_lut = get_backhaul_lut(iso3, country['region'], '2025')

    output = []

    for idx, region in regions.iterrows():

        sites_2G = lut['GSM'][region[gid_level]]
        sites_3G = lut['3G'][region[gid_level]]
        sites_4G = lut['4G'][region[gid_level]]
        total_sites = (sites_2G + sites_3G + sites_4G)

        backhaul_estimates = estimate_backhaul(total_sites, backhaul_lut)

        with rasterio.open(path_settlements) as src:

            affine = src.transform
            array = src.read(1)
            array[array <= 0] = 0

            population = [d['sum'] for d in zonal_stats(
                region['geometry'], array, stats=['sum'], nodata=0,
                affine=affine)][0]

        area_km2 = round(area_of_polygon(region['geometry']) / 1e6)

        output.append({
            'GID_0': region['GID_0'],
            gid_level: region[gid_level],
            'population': population,
            'area_km2': area_km2,
            'pop_density_km2': population / area_km2,
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

    path = os.path.join(DATA_INTERMEDIATE, iso3, 'sites', 'sites.csv')
    output.to_csv(path, index=False)

    return


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


def area_of_polygon(geom):
    """
    Returns the area of a polygon. Assume WGS84 as crs.

    """
    geod = pyproj.Geod(ellps="WGS84")

    poly_area, poly_perimeter = geod.geometry_area_perimeter(
        geom
    )

    return abs(poly_area)




# def estimate_backhaul(iso3, region, year):
#     """

#     """
#     output = []

#     path = os.path.join(BASE_PATH, 'raw', 'gsma', 'backhaul.csv')
#     backhaul_lut = pd.read_csv(path)
#     backhaul_lut = backhaul_lut.to_dict('records')

#     for item in backhaul_lut:
#         if region == item['Region'] and int(item['Year']) == int(year):
#             output.append({
#                 'tech': item['Technology'],
#                 'percentage': int(item['Value']),
#             })

#     return output


def estimate_backhaul_type(backhaul_lut):
    """
    Estimate backhaul type.

    """
    output = {}

    preference = [
        'fiber',
        'copper',
        'microwave',
        'satellite'
    ]

    perc_so_far = 0

    for tech in preference:
        for item in backhaul_lut:

            if tech == item['tech'].lower():
                perc = item['percentage']
                output[tech] = (perc + perc_so_far) / 100
                perc_so_far += perc

    return output


if __name__ == "__main__":

    technologies = [
        'GSM',
        '3G',
        '4G'
    ]

    for country in COUNTRY_LIST:

        if not country['iso3'] == 'COL':
            continue

        print('--Working on {}'.format(country['iso3']))

        process_unconstrained_site_estimation(country)

        # if country['iso3'] == 'CRI':
        #     print('Processing Costa Rica')
        #     process_costa_rica(country, technologies)

        # if country['iso3'] == 'GMB':
        #     print('Processing Gambia')
        #     process_the_gambia()

        # if country['iso3'] == 'SEN':
        #     print('Processing Senegal')
        #     process_senegal(country, technologies)
