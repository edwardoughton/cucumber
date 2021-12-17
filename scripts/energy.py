"""
Preprocess energy layers

Written by Ed Oughton.

June 2021

"""
import os
import configparser
import json
import csv
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.mask import mask
# from rasterstats import zonal_stats
from shapely.geometry import box

from countries import COUNTRY_PARAMETERS

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')


def cut_grid_finder_targets():
    """
    Take the global grid finder targets layer and cut out Chile.

    """
    iso3 = 'CHL'
    level = 3

    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'gridfinder_targets', 'tifs')

    if not os.path.exists(folder):
        os.makedirs(folder)

    path_targets = os.path.join(DATA_RAW, 'gridfinder', 'targets.tif')
    targets = rasterio.open(path_targets, 'r+')
    targets.nodata = 255
    targets.crs = {"init": "epsg:4326"}

    filename = 'regions_3_CHL.shp'
    path = os.path.join(DATA_INTERMEDIATE, iso3, 'regions', filename)
    regions = gpd.read_file(path, crs='epsg:4326')#[:1]

    for idx, region in regions.iterrows():

        GID_level = 'GID_{}'.format(level)
        GID_id = region[GID_level]

        filename = GID_id + '.tif'
        path_out = os.path.join(folder, filename)

        # if os.path.exists(path):
        #     continue

        geo_df = gpd.GeoDataFrame(geometry=gpd.GeoSeries(region['geometry']))

        bbox = geo_df.envelope

        geo = gpd.GeoDataFrame(
            {'geometry': bbox}, index=[0], crs='epsg:4326')

        coords = [json.loads(geo.to_json())['features'][0]['geometry']]

        #chop on coords
        out_img, out_transform = mask(targets, coords, crop=True)

        # Copy the metadata
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
                ]
            )

            if len(shapes_df) == 0:
                continue

            path_out = os.path.join(folder, '..', GID_id + '.shp')
            shapes_df.to_file(path_out, crs='epsg:4326')


def estimate_site_power_source():
    """
    Estimate the power source for each site.

    """
    iso3 = 'CHL'
    level = 3

    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'gridfinder_targets')

    filename = 'regions_3_CHL.shp'
    path = os.path.join(DATA_INTERMEDIATE, iso3, 'regions', filename)
    regions = gpd.read_file(path, crs='epsg:4326')#[:1]
    regions = regions.to_crs('epsg:3857')

    for idx, region in regions.iterrows():

        GID_level = 'GID_{}'.format(level)
        GID_id = region[GID_level]

        print('Working on {}'.format(GID_id))

        filename = GID_id + '.shp'
        path = os.path.join(DATA_INTERMEDIATE, iso3, 'sites', 'by_region', filename)

        output = []

        if os.path.exists(path):

            cells = gpd.read_file(path, crs='epsg:4326')#[:1]
            cells = cells.to_crs('epsg:3857')

            path = os.path.join(folder, GID_id + '.shp')

            if os.path.exists(path):

                targets = gpd.read_file(path, crs='epsg:4326')
                targets = targets.to_crs('epsg:3857')

                for idx, point in cells.iterrows():
                    distances = targets.distance(point['geometry']).tolist()
                    distances = [i for i in distances if i != 0]
                    if len(distances) == 0:
                        shortest_dist = 1e6
                    else:
                        shortest_dist = min(distances)
                    output.append({
                        'type': 'Feature',
                        'geometry': point['geometry'],
                        'properties': {
                            'closest_elec_target_m': shortest_dist,
                        }
                    })

        if len(output) == 0:
            continue

        output = gpd.GeoDataFrame.from_features(output, crs='epsg:3857')
        output = output.to_crs('epsg:4326')

        folder_out = os.path.join(DATA_INTERMEDIATE, iso3, 'sites', 'site_power')
        if not os.path.exists(folder_out):
            os.makedirs(folder_out)
        path_out = os.path.join(folder_out, GID_id + '.shp')
        output.to_file(path_out, crs='epsg:4326')


def write_all_sites_lut():
    """

    """
    iso3 = 'CHL'
    level = 3

    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'sites', 'site_power')

    filename = 'regions_3_CHL.shp'
    path = os.path.join(DATA_INTERMEDIATE, iso3, 'regions', filename)
    regions = gpd.read_file(path, crs='epsg:4326')#[:1]
    regions = regions.to_crs('epsg:3857')

    output = []

    for idx, region in regions.iterrows():

        GID_level = 'GID_{}'.format(level)
        GID_id = region[GID_level]

        path = os.path.join(folder, GID_id + '.shp')

        if os.path.exists(path):

            sites = gpd.read_file(path, crs='epsg:4326')

            for idx, site in sites.iterrows():
                output.append({
                    'GID_id': GID_id,
                    'GID_level': level,
                    #distance to the closest electricity point
                    'distance': site['closest_el'],
                })

    output = pd.DataFrame(output)
    path = os.path.join(folder, 'a_all_sites.csv')
    output.to_csv(path, index=False)


def write_site_lut():
    """

    """
    iso3 = 'CHL'
    level = 3

    folder = os.path.join(DATA_INTERMEDIATE, iso3, 'sites', 'site_power')
    filename = 'a_all_sites.csv'
    path = os.path.join(folder, filename)
    sites = pd.read_csv(path)#[:500]
    sites = sites.sort_values('distance')

    perc_ongrid = COUNTRY_PARAMETERS['energy']['perc_ongrid']
    # perc_other = COUNTRY_PARAMETERS['energy']['perc_other']

    quantity_ongrid = len(sites) * (perc_ongrid / 100)
    # quantity_other = len(sites) * (perc_other / 100)

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

    filename = 'regions_3_CHL.shp'
    path = os.path.join(DATA_INTERMEDIATE, iso3, 'regions', filename)
    regions = gpd.read_file(path, crs='epsg:4326')#[:5]
    unique_regions = regions['GID_3'].unique()

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


def process_solar_atlas():
    """
    Chop solar atlas into single files.

    """
    iso3 = 'CHL'

    folder_out = os.path.join(DATA_INTERMEDIATE, iso3, 'solar_atlas')

    if not os.path.exists(folder_out):
        os.makedirs(folder_out)

    folder_in = os.path.join(DATA_RAW, 'global_solar_atlas', 'monthly')
    files = os.listdir(folder_in)

    for filename in files:
        if not filename.endswith('.tif'):
            continue

        path_in = os.path.join(folder_in, filename)
        path_out = os.path.join(folder_out, filename)

        if os.path.exists(path_out):
            return print('Already processed solar atlas layer')

        targets = rasterio.open(path_in, 'r+')
        targets.nodata = 255
        targets.crs = {"init": "epsg:4326"}

        path_country = os.path.join(DATA_INTERMEDIATE, iso3,
            'national_outline.shp')

        if os.path.exists(path_country):
            country = gpd.read_file(path_country, crs='epsg:4326')
        else:
            print('Must generate national_outline.shp first' )

        bbox = country.total_bounds
        bbox = box(bbox[0], bbox[1], bbox[2], bbox[3])

        geo = gpd.GeoDataFrame({'geometry': bbox}, index=[0], crs='epsg:4326')

        coords = [json.loads(geo.to_json())['features'][0]['geometry']]

        #chop on coords
        out_img, out_transform = mask(targets, coords, crop=True)

        # Copy the metadata
        out_meta = targets.meta.copy()

        out_meta.update({"driver": "GTiff",
                        "height": out_img.shape[1],
                        "width": out_img.shape[2],
                        "transform": out_transform,
                        "crs": 'epsg:4326'})

        with rasterio.open(path_out, "w", **out_meta) as dest:
                dest.write(out_img)


# def energy_forcast():
#     """
#     Forcast the energy mix over the next n years.

#     """
#     output = []

#     iso3 = 'CHL'

#     on_grid_mix = {
#         'hydro': 31,
#         'oil': 22,
#         'gas': 17,
#         'coal': 18,
#         'renewables': 12,
#     }

#     growth_rate = {
#         'hydro': 2,
#         'oil': -2,
#         'gas': 1,
#         'coal': -2,
#         'renewables': 4,
#     }

#     timesteps = [t for t in range(2020, 2030 + 1, 1)]

#     for key1, value1 in on_grid_mix.items():

#         share = value1

#         for timestep in timesteps:

#             for key2, value2 in on_grid_mix.items():
#                 if key1 == key2:
#                     if timestep == 2020:
#                         share = share
#                     else:
#                         share = share + growth_rate[key1]

#                     output.append({
#                         'type': key1,
#                         'share': share,
#                         'year': timestep,
#                     })

#     output = pd.DataFrame(output)
#     folder = os.path.join(DATA_INTERMEDIATE, iso3, 'energy_forecast')
#     path = os.path.join(folder, 'energy_forecast.csv')
#     output.to_csv(path, index=False)


if __name__ == '__main__':

    # cut_grid_finder_targets()

    estimate_site_power_source()

    write_all_sites_lut()

    write_site_lut()

    # process_solar_atlas()

    # energy_forcast()
