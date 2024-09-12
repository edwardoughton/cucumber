"""
Collect and preprocess all necessary data.

Written by Ed Oughton.

March 2021.

"""
import os
import configparser
import json
import random
import numpy as np
import pandas as pd
import geopandas as gpd
import pyproj
from shapely.geometry import MultiPolygon
import rasterio
from rasterio.mask import mask
from rasterstats import zonal_stats

from misc import find_country_list

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, '..', '..', 'data_raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')


def process_country_shapes(country):
    """
    Creates a single national boundary for the desired country.

    Parameters
    ----------
    country : dict
        Contains all desired country information.

    """
    iso3 = country['iso3']

    path = os.path.join(DATA_INTERMEDIATE, iso3)

    if os.path.exists(os.path.join(path, 'national_outline.shp')):
        return 'Completed national outline processing'

    if not os.path.exists(path):
        os.makedirs(path)

    shape_path = os.path.join(path, 'national_outline.shp')

    path = os.path.join(DATA_RAW, 'gadm36_levels_shp', 'gadm36_0.shp')
    countries = gpd.read_file(path)

    single_country = countries[countries.GID_0 == iso3].reset_index()

    if not iso3 in ['MDV','COK','KIR','MHL','NIU']:
        single_country['geometry'] = single_country.apply(
            remove_small_shapes, axis=1)

    # print('Adding ISO country code and other global information')
    glob_info_path = os.path.join(BASE_PATH, 'global_information.csv')
    load_glob_info = pd.read_csv(glob_info_path, encoding = "ISO-8859-1",
        keep_default_na=False)
    # print(load_glob_info[load_glob_info['iso3'] == 'MDV'])
    # print(single_country.columns, load_glob_info.columns)
    single_country = single_country.merge(
        load_glob_info, left_on='GID_0', right_on='iso3')

    # print('Exporting processed country shape')
    single_country.to_file(shape_path, driver='ESRI Shapefile')

    return print('Processing country shape complete')


def process_regions(country):
    """
    Function for processing the lowest desired subnational
    regions for the chosen country.

    Parameters
    ----------
    country : dict
        Contains all desired country information.

    """
    regions = []

    iso3 = country['iso3']
    level = country['regional_level']

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

        regions = regions[regions.GID_0 == iso3]

        # exclusions = country['regions_to_exclude_GID_1']
        # regions = regions[~regions['GID_1'].astype(str).str.startswith(tuple(exclusions))]

        if not iso3 in ['MDV','COK','KIR','MHL','NIU']:
            regions['geometry'] = regions.apply(remove_small_shapes, axis=1)
        print(regions)
        try:
            regions.to_file(path_processed, driver='ESRI Shapefile')
        except:
            print('Unable to write {}'.format(filename))
            pass

    return


def process_settlement_layer(country):
    """
    Clip the settlement layer to the chosen country boundary
    and place in desired country folder.

    Parameters
    ----------
    country : dict
        Contains all desired country information.

    """
    iso3 = country['iso3']
    regional_level = country['regional_level']

    path_settlements = os.path.join(DATA_RAW,'settlement_layer',
        'ppp_2020_1km_Aggregated.tif')

    settlements = rasterio.open(path_settlements, 'r+')
    settlements.nodata = 255
    settlements.crs = {"init": "epsg:4326"}

    iso3 = country['iso3']
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


def get_regional_data(country):
    """
    Extract regional data including luminosity and population.

    Parameters
    ----------
    country : dict
        Contains all desired country information.

    """
    iso3 = country['iso3']
    level = country['regional_level']
    gid_level = 'GID_{}'.format(level)

    filename = 'population.csv'
    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'population')
    if not os.path.exists(folder):
        os.mkdir(folder)
    path_output = os.path.join(folder, filename)

    # if os.path.exists(path_output):
    #     return print('Regional data already exists')

    path_country = os.path.join(DATA_INTERMEDIATE, iso3,
        'national_outline.shp')

    single_country = gpd.read_file(path_country)

    path_settlements = os.path.join(DATA_INTERMEDIATE, iso3,
        'settlements.tif')

    if not iso3 in ['MDV','COK','KIR','MHL','NIU']:
        filename = 'regions_{}_{}.shp'.format(level, iso3)
        folder = os.path.join(DATA_INTERMEDIATE, iso3, 'regions')
        path = os.path.join(folder, filename)
        regions = gpd.read_file(path)#[:1]
    else:
        filename = 'national_outline.shp'
        folder = os.path.join(DATA_INTERMEDIATE, iso3)
        path = os.path.join(folder, filename)
        regions = gpd.read_file(path)#[:1]

    results = []

    for index, region in regions.iterrows():

        with rasterio.open(path_settlements) as src:

            affine = src.transform
            array = src.read(1)
            array[array <= 0] = 0
            
            if region['geometry'] == None:
                continue

            population_summation = [d['sum'] for d in zonal_stats(
                region['geometry'],
                array,
                stats=['sum'],
                nodata=0,
                affine=affine
                )][0]

        area_km2 = round(area_of_polygon(region['geometry']) / 1e6)

        if area_km2 == 0:
            continue

        if area_km2 > 0:
            population_km2 = (
                population_summation / area_km2 if population_summation else 0)
        else:
            population_km2 = 0

        results.append({
            'GID_0': region['GID_0'],
            'country_name': country['country_name'],
            'GID_id': region[gid_level],
            'GID_level': gid_level,
            'population': (population_summation if population_summation else 0),
            'area_km2': area_km2,
            'population_km2': population_km2,
        })

    results_df = pd.DataFrame(results)

    results_df.to_csv(path_output, index=False)

    print('Completed {}'.format(single_country.NAME_0.values[0]))

    return print('Completed regional data')


def area_of_polygon(geom):
    """
    Returns the area of a polygon. Assume WGS84 as crs.

    """
    geod = pyproj.Geod(ellps="WGS84")

    poly_area, poly_perimeter = geod.geometry_area_perimeter(
        geom
    )

    return abs(poly_area)


def remove_small_shapes(x):
    """
    Remove small multipolygon shapes.

    Parameters
    ---------
    x : polygon
        Feature to simplify.

    Returns
    -------
    MultiPolygon : MultiPolygon
        Shapely MultiPolygon geometry without tiny shapes.

    """
    # if its a single polygon, just return the polygon geometry
    if x.geometry.geom_type == 'Polygon':
        return x.geometry

    # if its a multipolygon, we start trying to simplify
    # and remove shapes if its too big.
    elif x.geometry.geom_type == 'MultiPolygon':

        area1 = 0.01
        area2 = 50

        # dont remove shapes if total area is already very small
        if x.geometry.area < area1:
            return x.geometry
        # remove bigger shapes if country is really big

        if x['GID_0'] in ['CHL','IDN']:
            threshold = 0.01
        elif x['GID_0'] in ['RUS','GRL','CAN','USA']:
            threshold = 0.01

        elif x.geometry.area > area2:
            threshold = 0.1
        else:
            threshold = 0.001

        # save remaining polygons as new multipolygon for
        # the specific country
        new_geom = []
        for y in x.geometry:
            if y.area > threshold:
                new_geom.append(y)

        return MultiPolygon(new_geom)


def process_unconstrained_site_estimation(country):
    """
    Allocate towers using an unconstrained site estimation process.

    """
    iso3 = country['iso3']
    level = country['regional_level']
    gid_level = 'GID_{}'.format(level)

    filename = 'population.csv'
    path = os.path.join(DATA_INTERMEDIATE, iso3, 'population', filename)
    regional_data = pd.read_csv(path)

    path = os.path.join(BASE_PATH, 'raw', 'site_counts', 'hybrid_site_data_v3.csv') #hybrid_site_data_v2
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

    #continent2 is missing from country metadata
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
            'GID_level': gid_level,
            # 'population': round(region['population']),
            # 'area_km2': round(region['area_km2']),
            'total_existing_sites': max(total_existing_sites_2G, total_existing_sites_4G),
            # 'total_estimated_sites_2G': round(total_existing_sites_2G),
            'total_existing_sites_4G': round(total_existing_sites_4G),
            # 'sites_estimated_2G_km2': round(total_existing_sites_2G / region['area_km2'],4),
            # 'sites_estimated_4G_km2': round(total_existing_sites_4G / region['area_km2'], 4),
            'backhaul_fiber': backhaul_estimates['backhaul_fiber'],
            # 'backhaul_copper': backhaul_estimates['backhaul_copper'],
            'backhaul_wireless': backhaul_estimates['backhaul_wireless'],
            # 'backhaul_satellite': backhaul_estimates['backhaul_satellite'],
        })

        if region['population'] == None:
            continue

        covered_pop_so_far_2G += region['population']
        covered_pop_so_far_4G += region['population']

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
            'total_existing_sites': int(site['total_existing_sites']),
            # 'total_estimated_sites_2G': int(site['total_estimated_sites_2G']),
            'total_existing_sites_4G': int(site['total_existing_sites_4G']),
            'backhaul_wireless': float(site['backhaul_wireless']),
            'backhaul_fiber':  float(site['backhaul_fiber']),
        }

    return output


def generate_deciles(country):
    """
    Generate decile data. 

    """
    folder = os.path.join(DATA_INTERMEDIATE, country['iso3'], 'sites')
    sites1 = os.path.join(folder, 'sites.csv')
    sites_lut = load_sites(country, sites1)

    filename = 'population.csv'
    path = os.path.join(DATA_INTERMEDIATE, country['iso3'], 'population', filename)
    data_initial = load_regions(country, path, sites_lut)#[:50]

    data = aggregate_to_deciles(data_initial)
    filename = 'decile_data.csv'
    path_out = os.path.join(DATA_INTERMEDIATE, country['iso3'], filename)
    data.to_csv(path_out, index=False)
    
    return


def load_regions(country, path, sites_lut):
    """
    Load country regions.

    """
    data_initial = []

    regions = pd.read_csv(path)
    regions = regions[regions['population'] > 0]
    regions = regions.sort_values(by='population_km2', ascending=True)

    if not country['iso3'] in ['MDV','COK','KIR','MHL','NIU']:
        deciles = [10,9,8,7,6,5,4,3,2,1]
        regions['decile'] = pd.qcut(regions['population_km2'],
            q=10,
            labels=deciles,
            duplicates='drop'
            )
    else:
        n = len(regions)
        regions.insert(len(regions.columns), 'decile', range(1, n + 1))

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
                    'total_existing_sites': value['total_existing_sites'],
                    'total_existing_sites_4G': value['total_existing_sites_4G'],
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
        total_existing_sites = 0
        total_existing_sites_4G = 0
        backhaul_wireless = 0
        backhaul_fiber = 0
        on_grid_perc = []
        grid_other_perc = []

        for item in data_initial:

            if not decile == item['decile']:
                continue

            population_total += item['population_total']
            area_km2 += item['area_km2']
            total_existing_sites += item['total_existing_sites']
            total_existing_sites_4G += item['total_existing_sites_4G']
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
            'total_existing_sites': total_existing_sites,
            'total_existing_sites_4G': total_existing_sites_4G,
            'backhaul_wireless': backhaul_wireless,
            'backhaul_fiber': backhaul_fiber,
            'on_grid_perc': sum(on_grid_perc)/len(on_grid_perc),
            'grid_other_perc': sum(grid_other_perc)/len(grid_other_perc),
        })

    output = pd.DataFrame(output)

    output['geotype'] = output.apply(define_geotype, axis=1)

    return output


def get_regional_data_lut(country):
    """
    Export decile information for use later in visualization.
    
    """
    output = []

    # if not country['iso3'] == 'GBR':
    #     continue

    # if country['iso3'] in ['MAC', 'STP', 'WLF']:
    #     continue

    filename = 'population.csv'
    folder = os.path.join(DATA_INTERMEDIATE, country['iso3'], 'population')
    path = os.path.join(folder, filename)

    if not os.path.exists(path):
        return

    data = pd.read_csv(path)
    data = data[data['population'] > 0 ]
    data = data.sort_values(by='population_km2', ascending=True)

    if not country['iso3'] in ['MDV','COK','KIR','MHL','NIU']:
        deciles = [10,9,8,7,6,5,4,3,2,1]
        data['decile'] = pd.qcut(data['population_km2'],
            q=10,
            labels=deciles,
            duplicates='drop'
            )
    else:
        n = len(data)
        data.insert(len(data.columns), 'decile', range(1, n + 1))

    data['satellite'] = np.where(data['population_km2'] < 5, 1, 0)

    filename = 'regional_data_deciles.csv'
    folder = os.path.join(DATA_INTERMEDIATE, country['iso3'], 'population')
    path = os.path.join(folder, filename)
    data.to_csv(path, index=False)

    return


if __name__ == '__main__':

    countries = find_country_list([])
    countries = countries

    for country in countries:

        # if not country['iso3'] == 'PLW':
        #     continue
        if "{}".format(country['adb_region']) == 'nan':
            continue
        print(country['adb_region'])
        print('----')
        print('-- Working on {}'.format(country['country_name']))

        # process_country_shapes(country)

        # process_regions(country)

        # process_settlement_layer(country)

        get_regional_data(country)

        # process_unconstrained_site_estimation(country)

        generate_deciles(country)

        get_regional_data_lut(country)
