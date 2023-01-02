"""
Prepare deciles.

"""
import os
import configparser
# import json
# import csv
import pandas as pd
# import geopandas as gpd
# import pyproj
# from shapely.geometry import Polygon, MultiPolygon, mapping, shape, MultiLineString, LineString
# from shapely.ops import transform, unary_union, nearest_points
# import fiona
# import fiona.crs
# import rasterio
# from rasterio.mask import mask
# from rasterstats import zonal_stats
# import networkx as nx
# from rtree import index
# import numpy as np
# import random
# import math
# from tqdm import tqdm

from misc import find_country_list

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')


def load_sites(country, sites):
    """
    Load sites lookup table.

    """
    gid_id = 'GID_{}'.format(country['regional_level'])

    output = {}

    sites = pd.read_csv(sites)

    for idx, site in sites.iterrows():
        output[site[gid_id]] = {
            'GID_0': site['GID_0'],
            # 'sites_2G': int(site1['sites_2G']),
            # 'sites_3G': int(site1['sites_3G']),
            # 'sites_4G': int(site['sites_4G']),
            'total_estimated_sites': int(site['total_estimated_sites']),
            'total_estimated_sites_2G': int(site['total_estimated_sites_2G']),
            'total_estimated_sites_4G': int(site['total_estimated_sites_4G']),
            'backhaul_wireless': float(site['backhaul_wireless']),
            'backhaul_fiber':  float(site['backhaul_fiber']),
            # 'on_grid_perc': float(site['on_grid_perc']),
            # 'grid_other_perc': float(site['grid_other_perc']),
            # 'total_sites': site['total_sites'],
        }

    return output


def load_regions(country, path, sites_lut):
    """
    Load country regions.

    """
    data_initial = []

    regions = pd.read_csv(path)

    regions = regions.sort_values(by='population_km2', ascending=True)

    deciles = [10,9,8,7,6,5,4,3,2,1]
    regions['decile'] = pd.qcut(regions['population_km2'],
        q=10,
        labels=deciles,
        duplicates='drop'
        )

    regions = regions.to_dict('records')

    for item in regions:
        for key, value in sites_lut.items():
            if item['GID_id'] == key:
                data_initial.append({
                    'GID_0': item['GID_0'],
                    'GID_id': item['GID_id'],
                    'GID_level': item['GID_level'],
                    'population_total': item['population'],
                    'area_km2': item['area_km2'],
                    # 'population_km2': item['population_km2'],
                    # 'mean_luminosity_km2': item['mean_luminosity_km2'],
                    'decile': item['decile'],
                    # 'geotype': item['geotype'],
                    # 'sites_4G': value['sites_4G'],
                    'total_estimated_sites': value['total_estimated_sites'],
                    'total_estimated_sites_4G': value['total_estimated_sites_4G'],
                    'backhaul_wireless': value['backhaul_wireless'],
                    'backhaul_fiber': value['backhaul_fiber'],
                    'on_grid_perc': 95, #value['on_grid_perc'],
                    'grid_other_perc': 5, #value['grid_other_perc'],
                })

    return data_initial


def define_geotype(x):
    """
    Allocate geotype given a specific population density.

    """
    if x['population_km2'] > 5000:
        return 'urban'
    elif x['population_km2'] > 1500:
        return 'suburban 1'
    elif x['population_km2'] > 1000:
        return 'suburban 2'
    elif x['population_km2'] > 500:
        return 'rural 1'
    elif x['population_km2'] > 100:
        return 'rural 2'
    elif x['population_km2'] > 50:
        return 'rural 3'
    elif x['population_km2'] > 10:
        return 'rural 4'
    else:
        return 'rural 5'


def aggregate_to_deciles(data_initial):
    """

    """
    unique_deciles = set()
    for item in data_initial:
        unique_deciles.add(item['decile'])

    output = []

    for decile in list(unique_deciles):

        population_total = 0
        area_km2 = 0
        total_estimated_sites = 0
        total_estimated_sites_4G = 0
        backhaul_wireless = 0
        backhaul_fiber = 0
        on_grid_perc = []
        grid_other_perc = []

        for item in data_initial:

            if not decile == item['decile']:
                continue

            population_total += item['population_total']
            area_km2 += item['area_km2']
            total_estimated_sites += item['total_estimated_sites']
            total_estimated_sites_4G += item['total_estimated_sites_4G']
            backhaul_wireless += item['backhaul_wireless']
            backhaul_fiber += item['backhaul_fiber']
            on_grid_perc.append(item['on_grid_perc'])
            grid_other_perc.append(item['grid_other_perc'])

        output.append({
            'GID_0': item['GID_0'],
            'decile': decile,
            'population_total': population_total,
            'area_km2': area_km2,
            'population_km2': round(population_total / area_km2, 4),
            'total_estimated_sites': total_estimated_sites,
            'total_estimated_sites_4G': total_estimated_sites_4G,
            'backhaul_wireless': backhaul_wireless,
            'backhaul_fiber': backhaul_fiber,
            'on_grid_perc': sum(on_grid_perc)/len(on_grid_perc),
            'grid_other_perc': sum(grid_other_perc)/len(grid_other_perc),
        })

    output = pd.DataFrame(output)

    output['geotype'] = output.apply(define_geotype, axis=1)

    return output


if __name__ == '__main__':

    countries = find_country_list([])

    for country in countries:

        # if not country['iso3'] == 'GBR':
        #     continue

        print('Working on {}'.format(country['iso3']))

        folder = os.path.join(DATA_INTERMEDIATE, country['iso3'], 'sites')
        sites1 = os.path.join(folder, 'sites.csv')
        sites_lut = load_sites(country, sites1)

        filename = 'regional_data.csv'
        path = os.path.join(DATA_INTERMEDIATE, country['iso3'], filename)
        data_initial = load_regions(country, path, sites_lut)#[:50]

        data = aggregate_to_deciles(data_initial)
        filename = 'decile_data.csv'
        path_out = os.path.join(DATA_INTERMEDIATE, country['iso3'], filename)
        data.to_csv(path_out, index=False)
