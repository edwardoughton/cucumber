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

        filename = 'CELLID_2021_03_' + GID_id + '.shp'
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



if __name__ == '__main__':

    # cut_grid_finder_targets()

    estimate_site_power_source()

    # process_solar_atlas()
