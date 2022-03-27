"""
Preprocess energy layers

Written by Ed Oughton.

June 2021

"""
import os
import configparser
import json
import csv
import math
import pandas as pd
import geopandas as gpd
import rasterio
from rasterio.mask import mask
# from rasterstats import zonal_stats
from shapely.geometry import box
from random import uniform

from countries import COUNTRY_PARAMETERS

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')


def find_country_list(continent_list):
    """
    This function produces country information by continent.

    Parameters
    ----------
    continent_list : list
        Contains the name of the desired continent, e.g. ['Africa']

    Returns
    -------
    countries : list of dicts
        Contains all desired country information for countries in
        the stated continent.

    """
    glob_info_path = os.path.join(BASE_PATH, 'global_information.csv')

    countries = pd.read_csv(glob_info_path, encoding = "ISO-8859-1")

    if len(continent_list) > 0:
        subset = countries.loc[countries['continent'].isin(continent_list)]
    else:
        subset = countries

    countries = []

    for index, country in subset.iterrows():

        countries.append({
            'country_name': country['country'],
            'iso3': country['ISO_3digit'],
            'iso2': country['ISO_2digit'],
            'regional_level': country['lowest'],
        })

    return countries


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
        sites_estimated_km2 = sites_subset['sites_estimated_km2'].values[0]

        #Get the density of area with electricity
        target_density_km2 = target_area_km2 / region_area_km2

        total_estimated_sites = sites_subset['total_estimated_sites']

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

    os.environ['GDAL_DATA'] = ("C:\\Users\edwar\Anaconda3\Library\share\gdal")

    countries = find_country_list([])

    for country in countries:#[:1]:

        if not country['iso3'] == 'COL':
            continue

        print('-- Working on {}'.format(country['country_name']))

        cut_grid_finder_targets(country)

        estimate_site_power_source(country)

        write_site_lut(country)

        # process_solar_atlas()
