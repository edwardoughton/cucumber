"""
Read in available site data

Written by Ed Oughton

21st April 2020

"""
import os
import csv
import configparser
import json
import pandas as pd
import geopandas as gpd
# import xlrd
import numpy as np
from shapely.geometry import MultiPolygon
from shapely.ops import transform, unary_union
import rasterio
from rasterio.mask import mask
from rasterstats import zonal_stats
import pyproj
import random
import math
from random import uniform

# from countries import COUNTRY_LIST, COUNTRY_PARAMETERS
from misc import find_country_list

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
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

    path = os.path.join(DATA_RAW, 'site_counts', 'hybrid_site_data.csv')
    site_data = pd.read_csv(path, encoding = "ISO-8859-1")

    population = regional_data['population'].sum()

    site_data['estimated_towers'] = pd.to_numeric(site_data['estimated_towers'])

    site_data = site_data.loc[site_data['ISO3'] == iso3]
    if len(site_data) >= 1:
        coverage_2G = site_data['coverage_2G_perc'].sum()
        coverage_4G = site_data['coverage_4G_perc'].sum()
        towers = site_data['estimated_towers'].sum()
    else:
        coverage_2G = 0
        coverage_4G = 0
        towers = 0

    population_covered_2G = population * (coverage_2G / 100)
    population_covered_4G = population * (coverage_4G / 100)

    if population_covered_2G < population_covered_4G:
        population_covered_2G = population_covered_4G

    towers_2G = towers * (coverage_2G / 100)
    if np.isnan(towers_2G) or population_covered_2G == 0 or towers_2G == 0:
        towers_2G = 0
        towers_per_pop_2G = 0
    else:
        towers_per_pop_2G = towers_2G / population_covered_2G

    towers_4G = towers * (coverage_4G / 100)
    if np.isnan(towers_4G) or population_covered_4G == 0 or towers_4G == 0:
        towers_4G = 0
        towers_per_pop_4G = 0
    else:
        towers_per_pop_4G = towers_4G / population_covered_4G

    backhaul_lut = get_backhaul_lut(iso3, country['continent2'], '2025')

    regional_data = regional_data.to_dict('records')
    data = sorted(regional_data, key=lambda k: k['population_km2'], reverse=True)

    output = []

    covered_pop_so_far = 0
    covered_pop_so_far_2G = 0
    covered_pop_so_far_4G = 0

    for region in data:

        if covered_pop_so_far_2G < population_covered_2G:
            total_existing_sites_2G = round(region['population'] * towers_per_pop_2G)
        else:
            total_existing_sites_2G = 0

        if covered_pop_so_far_4G < population_covered_4G:
            total_existing_sites_4G = round(region['population'] * towers_per_pop_4G)
        else:
            total_existing_sites_4G = 0

        backhaul_estimates = estimate_backhaul(total_existing_sites_2G, backhaul_lut)

        output.append({
            'GID_0': region['GID_0'],
            region['GID_level']: region['GID_id'],
            'population': round(region['population']),
            'area_km2': round(region['area_km2']),
            'total_estimated_sites': max(total_existing_sites_2G, total_existing_sites_4G),
            'total_estimated_sites_2G': round(total_existing_sites_2G),
            'total_estimated_sites_4G': round(total_existing_sites_4G),
            'sites_estimated_2G_km2': round(total_existing_sites_2G / region['area_km2'],4),
            'sites_estimated_4G_km2': round(total_existing_sites_4G / region['area_km2'], 4),
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


def cut_grid_finder_targets(country):
    """
    Take the global grid finder targets layer and cut out.

    """
    iso3 = country['iso3']
    level = country['regional_level']

    folder_tifs = os.path.join(DATA_INTERMEDIATE, iso3, 'gridfinder_targets', 'tifs')

    if not os.path.exists(folder_tifs):
        os.makedirs(folder_tifs)

    folder_shps = os.path.join(DATA_INTERMEDIATE, iso3, 'gridfinder_targets', 'shapes')

    if not os.path.exists(folder_shps):
        os.makedirs(folder_shps)

    path_targets = os.path.join(DATA_RAW, 'gridfinder', 'targets.tif')
    targets = rasterio.open(path_targets, 'r+')
    targets.nodata = 255
    targets.crs = {"init": "epsg:4326"}

    filename = 'regions_{}_{}.shp'.format(level, iso3)
    path = os.path.join(DATA_INTERMEDIATE, iso3, 'regions', filename)
    regions = gpd.read_file(path, crs='epsg:4326')#[:1]

    filename = 'gridfinder_targets_lut.csv'
    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'gridfinder_targets')
    path_out = os.path.join(folder, filename)

    if os.path.exists(path_out):
        return

    csv_output = []

    for idx, region in regions.iterrows():

        GID_level = 'GID_{}'.format(level)
        GID_id = region[GID_level]

        # if not GID_id == 'COL.14.100_1':
        #     continue

        filename = GID_id + '.tif'
        path_out = os.path.join(folder_tifs, filename)

        geo_df = gpd.GeoDataFrame(
            geometry=gpd.GeoSeries(region['geometry']),
            crs='epsg:4326')

        geo_df_3857 = geo_df.to_crs(3857)
        geo_df_3857['area_km2'] = geo_df_3857['geometry'].area / 1e6
        region_area_km2 = geo_df_3857['area_km2'].sum()

        bbox = geo_df.envelope

        geo = gpd.GeoDataFrame(
            {'geometry': bbox}, index=[0], crs='epsg:4326')

        coords = [json.loads(geo.to_json())['features'][0]['geometry']]

        out_img, out_transform = mask(targets, coords, crop=True)

        out_meta = targets.meta.copy()

        out_meta.update({"driver": "GTiff",
                        "height": out_img.shape[1],
                        "width": out_img.shape[2],
                        "transform": out_transform,
                        "crs": 'epsg:4326'})

        with rasterio.open(path_out, "w", **out_meta) as dest:
                dest.write(out_img)

        with rasterio.open(path_out) as src:
            data = src.read()
            polygons = rasterio.features.shapes(data, transform=src.transform)
            shapes_df = gpd.GeoDataFrame.from_features(
                [
                    {'geometry': poly, 'properties':{'value':value}}
                    for poly, value in polygons
                    if value == 1
                ], crs='epsg:4326'
            )

            if len(shapes_df) == 0:
                continue

            path_out = os.path.join(folder_shps, '..', GID_id + '.shp')
            shapes_df.to_file(path_out, crs='epsg:4326')

            shapes_df = shapes_df.to_crs(3857)
            shapes_df['area_km2'] = shapes_df['geometry'].area/1e6
            shapes_df = shapes_df.to_dict('records')

            target_area_km2 = 0

            for item in shapes_df:
                target_area_km2 += item['area_km2']

            csv_output.append({
                'country_name': region['NAME_0'],
                'iso3': region['GID_0'],
                '{}'.format(GID_level): '{}'.format(GID_id),
                'region_area_km2': region_area_km2,
                'target_area_km2': target_area_km2
            })

    csv_output = pd.DataFrame(csv_output)
    csv_output.to_csv(path_out, index=False)


def estimate_site_power_source(country):
    """
    Estimate the power source for each site.

    """
    iso3 = country['iso3']
    level = country['regional_level']

    path = os.path.join(DATA_INTERMEDIATE, iso3, 'sites', 'sites.csv')
    sites = pd.read_csv(path)

    filename = 'gridfinder_targets_lut.csv'
    path = os.path.join(DATA_INTERMEDIATE, iso3, 'gridfinder_targets', filename)
    targets = pd.read_csv(path)

    filename = 'regions_{}_{}.shp'.format(level, iso3)
    path = os.path.join(DATA_INTERMEDIATE, iso3, 'regions', filename)
    regions = gpd.read_file(path, crs='epsg:4326')#[:20]
    # regions = regions.to_crs('epsg:3857')

    output = []

    for idx, region in regions.iterrows():

        GID_level = 'GID_{}'.format(level)
        GID_id = region[GID_level]

        sites_subset = sites.loc[sites[GID_level] == region[GID_level]]
        targets_subset = targets.loc[targets[GID_level] == region[GID_level]]

        if len(targets_subset) == 0:
            continue

        target_area_km2 = targets_subset['target_area_km2'].values[0]
        region_area_km2 = targets_subset['region_area_km2'].values[0]

        #Get the density of sites
        sites_estimated_km2 = sites_subset['sites_estimated_2G_km2'].values[0]

        #Get the density of area with electricity
        target_density_km2 = target_area_km2 / region_area_km2

        total_estimated_sites = sites_subset['total_estimated_sites_2G']

        for i in range(1, total_estimated_sites.values[0] + 1):

            # Get the mean half point distance between points
            # https://felix.rohrba.ch/en/2015/point-density-and-point-spacing/
            distance = math.sqrt(1/target_density_km2)

            rand = uniform(0, distance)

            total_distance = distance + rand

            output.append({
                'GID_id': GID_id,
                'GID_level': GID_level,
                'distance': total_distance * 1e3,
                'rand': rand * 1e3,
            })

    folder_out = os.path.join(DATA_INTERMEDIATE, iso3, 'sites', 'site_power')
    if not os.path.exists(folder_out):
        os.makedirs(folder_out)
    path_out = os.path.join(folder_out, 'a_all_sites.csv')
    output = pd.DataFrame(output)
    output.to_csv(path_out)


def write_site_lut(country):
    """

    """
    iso3 = country['iso3']
    level = country['regional_level']

    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'sites', 'site_power')
    filename = 'a_all_sites.csv'
    path = os.path.join(folder, filename)
    sites = pd.read_csv(path)#[:500]
    sites = sites.sort_values('distance')

    perc_ongrid = COUNTRY_PARAMETERS[iso3]['energy']['perc_ongrid']

    quantity_ongrid = len(sites) * (perc_ongrid / 100)

    interim = []
    count = 1

    for idx, site in sites.iterrows():

        if count == round(quantity_ongrid):
            print('Break distance is {}'.format(round(site['distance'])))

        if count <= quantity_ongrid:
            grid_type = 'on_grid'
        else:
            grid_type = 'grid_other'

        interim.append({
            'GID_id': site['GID_id'],
            'GID_level': site['GID_level'],
            'distance': site['distance'],
            'grid_type': grid_type,
        })

        count += 1

    filename = 'regions_{}_{}.shp'.format(level, iso3)
    path = os.path.join(DATA_INTERMEDIATE, iso3, 'regions', filename)
    regions = gpd.read_file(path, crs='epsg:4326')#[:5]
    unique_regions = regions['GID_{}'.format(level)].unique()

    interim_df = pd.DataFrame(interim)
    path = os.path.join(folder, 'interim_df.csv')
    interim_df.to_csv(path, index=False)

    output = []

    for region in unique_regions:

        distances = []
        on_grid = 0
        grid_other = 0
        total = 0

        for site in interim:
            if region == site['GID_id']:
                distances.append(site['distance'])
                if site['grid_type'] == 'on_grid':
                    on_grid += 1
                    total += 1
                else:
                    grid_other += 1
                    total += 1
        if total == 0:
            continue

        output.append({
            'GID_id': region,
            'GID_level': level,
            'dist_mean': (sum(distances) / total),#dist_mean,
            'on_grid_perc': (on_grid / total) * 100,
            'grid_other_perc': (grid_other / total) * 100,
            'total_sites': total,
        })

    output = pd.DataFrame(output)
    path = os.path.join(folder, 'b_site_power_lut.csv')
    output.to_csv(path, index=False)


def combine_sites(country):
    """

    """
    folder = os.path.join(DATA_INTERMEDIATE, country['iso3'], 'sites')
    sites1 = os.path.join(folder, 'sites.csv')
    sites2 = os.path.join(folder, 'site_power', 'b_site_power_lut.csv')

    output = []

    GID_id = 'GID_{}'.format(country['regional_level'])

    sites1 = pd.read_csv(sites1)
    sites2 = pd.read_csv(sites2)

    for idx, site1 in sites1.iterrows():
        for idx, site2 in sites2.iterrows():
            if site1[GID_id] == site2['GID_id']:
                output.append({
                    'GID_0': site1['GID_0'],
                    'GID_id': site2['GID_id'],
                    # 'sites_2G': int(site1['sites_2G']),
                    # 'sites_3G': int(site1['sites_3G']),
                    'sites_4G': int(site1['total_estimated_sites_4G']),
                    'total_estimated_sites': int(site1['total_estimated_sites_2G']),
                    'backhaul_wireless': float(site1['backhaul_wireless']),
                    'backhaul_fiber':  float(site1['backhaul_fiber']),
                    'on_grid_perc': float(site2['on_grid_perc']),
                    'grid_other_perc': float(site2['grid_other_perc']),
                    'total_sites': site2['total_sites'],
                })

    output = pd.DataFrame(output)
    path = os.path.join(folder, 'sites.csv')
    output.to_csv(path, index=False)

    return


if __name__ == "__main__":

    countries = find_country_list([])

    for country in countries:
        # print(country)
        # if not country['iso3'] in ['BRA', 'CAN', 'DNK', 'EGY', 'JPN', 'KEN', 'MLT', 'PHL', 'RUS', 'ARE','URY']:
        #     continue

        # if not country['iso3'] == 'GBR':
        #     continue

        print('--Working on {}'.format(country['iso3']))

        process_unconstrained_site_estimation(country)

        # cut_grid_finder_targets(country)

        # estimate_site_power_source(country)

        # write_site_lut(country)

        # combine_sites(country)
