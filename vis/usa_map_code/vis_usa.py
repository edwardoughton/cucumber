"""
Plot spatial data. 

Written by Ed Oughton.

June 2024.

"""
import os
import sys
import configparser
# import json
# import csv
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
# import contextily as ctx
# import openpyxl
# import xlwings as xw

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), '..', 'scripts', 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')
RESULTS = os.path.join(BASE_PATH, '..', 'results')
VIS = os.path.join(BASE_PATH, '..', 'vis', 'figures')

sys.path.insert(1, os.path.join(BASE_PATH, '..', 'scripts'))
from misc import find_country_list

# def find_country_list(continent_list):
#     """
#     This function produces country information by continent.

#     Parameters
#     ----------
#     continent_list : list
#         Contains the name of the desired continent, e.g. ['Africa']

#     Returns
#     -------
#     countries : list of dicts
#         Contains all desired country information for countries in
#         the stated continent.

#     """
#     glob_info_path = os.path.join(BASE_PATH, 'global_information.csv')
#     countries = pd.read_csv(glob_info_path, encoding = "ISO-8859-1")

#     if len(continent_list) > 0:
#         data = countries.loc[countries['continent'].isin(continent_list)]
#     else:
#         data = countries

#     output = []

#     for index, country in data.iterrows():

#         output.append({
#             'country_name': country['country'],
#             'iso3': country['ISO_3digit'],
#             'iso2': country['ISO_2digit'],
#             'regional_level': country['lowest'],
#             # 'imf': country['imf']
#         })

#     return output


def get_country_outlines(countries):
    """

    """
    imf_iso3_codes = []

    for item in countries:
        if item['imf'] == 1:
            imf_iso3_codes.append(item['iso3'])

    path = os.path.join(DATA_RAW, 'gadm36_levels_shp', 'gadm36_0.shp')
    country_shapes = gpd.read_file(path, crs='epsg:4326')

    imf_countries = country_shapes[country_shapes['GID_0'].isin(imf_iso3_codes)]

    return imf_countries


def get_non_imf_outlines(countries):
    """

    """
    non_imf_iso3_codes = []

    for item in countries:
        if not item['imf'] == 1:
            non_imf_iso3_codes.append(item['iso3'])

    path = os.path.join(DATA_RAW, 'gadm36_levels_shp', 'gadm36_0.shp')
    country_shapes = gpd.read_file(path, crs='epsg:4326')

    non_imf = country_shapes[country_shapes['GID_0'].isin(non_imf_iso3_codes)]

    return non_imf


def collect_results(countries):
    """
    Collect results.

    """
    output = {}

    for country in countries:

        interim = {}

        filename = "results_{}.csv".format(country['iso3'])
        folder = os.path.join(RESULTS, 'model_results', country['iso3'])
        path = os.path.join(folder, filename)
        data = pd.read_csv(path)
        data['emissions_per_smartphone_kg'] = (
            ((data['total_existing_emissions_t_co2'] + 
            data['total_new_emissions_t_co2']) * 1e3) /
            data['population_with_smartphones']
        )
        # data['total_emissions_kg'] = (
        #     data['emissions_per_smartphone_kg'] * 
        #     data['population_with_smartphones']
        # )
        data = data[['decile','emissions_per_smartphone_kg']]
        data = data.to_dict('records')

        for item in data:
            interim[item['decile']] = item['emissions_per_smartphone_kg']

        output[country['iso3']] = interim

    return output


def correct_decile(key1):
    """

    """
    if 'Decile 10' in key1:
        key1 = 100
    elif 'Decile 9' in key1:
        key1 = 90
    elif 'Decile 8' in key1:
        key1 = 80
    elif 'Decile 7' in key1:
        key1 = 70
    elif 'Decile 6' in key1:
        key1 = 60
    elif 'Decile 5' in key1:
        key1 = 50
    elif 'Decile 4' in key1:
        key1 = 40
    elif 'Decile 3' in key1:
        key1 = 30
    elif 'Decile 2' in key1:
        key1 = 20
    elif 'Decile 1' in key1:
        key1 = 10

    return key1


def collect_deciles(countries):
    """
    Collect all decile information.

    """
    path_out = os.path.join(VIS, '..', 'data', 'global_deciles.csv')

    # if os.path.exists(path_out):
    #     output = pd.read_csv(path_out)
    #     return output

    results_dict = collect_results(countries)#cost_[:100]

    output = []

    for country in countries:#[:1]:

        # if not country['iso3'] == 'GBR':
        #     continue

        country_results = results_dict[country['iso3']]

        filename = "regional_data_deciles.csv"
        folder = os.path.join(DATA_INTERMEDIATE, country['iso3'], 'population')
        path = os.path.join(folder, filename)
        if not os.path.exists(path):
            continue
        data = pd.read_csv(path)
        data = data.to_dict('records')

        for item in data:

            emissions_per_smartphone_kg = country_results[item['decile']]

            penetration_rate = 1
            total_emissions = round(
                (item['population'] * penetration_rate) * 
                emissions_per_smartphone_kg, 1
            )

            output.append({
                # 'GID_0': item['GID_0'],
                'GID_id': item['GID_id'],
                # 'GID_level': item['GID_level'],
                'population': item['population'],
                'area_km2': item['area_km2'],
                'pop_density_km2': item['population'] / item['area_km2'],
                'emissions_kg': total_emissions,
                'decile': item['decile'],
            })

    output = pd.DataFrame(output)
    output.to_csv(path_out, index=False)

    return output


def get_regional_shapes():
    """
    Load regional shapes.
    """
    filename = 'regions.shp'
    folder = os.path.join(VIS, '..', 'data')
    if not os.path.exists(folder):
        os.makedirs(folder)
    path = os.path.join(folder, filename)

    if os.path.exists(path):
        output = gpd.read_file(path)
        # output = output[output['GID_id'].str.startswith('AFG')]
        return output

    output = []

    for item in os.listdir(DATA_INTERMEDIATE):#[:10]:
        if len(item) == 3: # we only want iso3 code named folders

            filename_gid3 = 'regions_3_{}.shp'.format(item)
            path_gid3 = os.path.join(DATA_INTERMEDIATE, item, 'regions', filename_gid3)

            filename_gid2 = 'regions_2_{}.shp'.format(item)
            path_gid2 = os.path.join(DATA_INTERMEDIATE, item, 'regions', filename_gid2)

            filename_gid1 = 'regions_1_{}.shp'.format(item)
            path_gid1 = os.path.join(DATA_INTERMEDIATE, item, 'regions', filename_gid1)

            if os.path.exists(path_gid3):
                data = gpd.read_file(path_gid3)
                data['GID_id'] = data['GID_3']
                data = data.to_dict('records')
            elif os.path.exists(path_gid2):
                data = gpd.read_file(path_gid2)
                data['GID_id'] = data['GID_2']
                data = data.to_dict('records')
            elif os.path.exists(path_gid1):
                data = gpd.read_file(path_gid1)
                data['GID_id'] = data['GID_1']
                data = data.to_dict('records')
            else:
                print('No shapefiles for {}'.format(item))
                continue

            for datum in data:
                output.append({
                    'geometry': datum['geometry'],
                    'properties': {
                        'GID_id': datum['GID_id'],
                        # 'area_km2': datum['area_km2']
                    },
                })

    output = gpd.GeoDataFrame.from_features(output, crs='epsg:4326')
    output.to_file(path)

    return output


def combine_data(deciles, regions):
    """

    """
    regions['iso3'] = regions['GID_id'].str[:3]
    regions = regions[['GID_id', 'iso3', 'geometry']] #[:1000]
    regions = regions.copy()

    regions = regions.merge(deciles, how='left', left_on='GID_id', right_on='GID_id')
    # regions.reset_index(drop=True, inplace=True)
    # regions.to_file(os.path.join(VIS,'..','data','test3.shp'))

    return regions


def plot_regions_by_emissions(regions, path): #, imf_countries, non_imf):
    """
    Plot regions by cost.

    """
    regions['emissions'] = round(regions['emissions_'] / 1e3,2)
    regions = regions[['geometry','emissions']]
    regions['emissions'] = regions['emissions'].fillna(0)
    # regions.to_file(os.path.join(VIS,'..','data','test4.shp'))

    # satellite = regions[regions['GID_0'].isna()]

    regions = regions.dropna()
    # zeros = regions[regions['cost'] == 0]
    # regions = regions[regions['cost'] != 0]

    # bins = [0,10,20,30,40,50,60,70,80,90,1e12]
    bins = [0,5,10,15,20,25,30,35,40,45,1e12]
    # bins = [0,1,2,3,4,5,6,7,8,9,1e12]
    # labels = ['$<5t CO_2$','$20m','$30m','$40m','$50m','$60m','$70m','$80m','$90m','>$100m']
    labels = [
        '<5t $CO_2$',
        '<10t $CO_2$',
        '<15t $CO_2$',
        '<20t $CO_2$',
        '<25t $CO_2$',
        '<30t $CO_2$',
        '<35t $CO_2$',
        '<40t $CO_2$',
        '<45t $CO_2$',
        '>45t $CO_2$'
    ]
    regions['bin'] = pd.cut(
        regions['emissions'],
        bins=bins,
        labels=labels
    )

    sns.set(font_scale=0.9)
    fig, ax = plt.subplots(3, 2, figsize=(12, 5))

    # minx, miny, maxx, maxy = regions.total_bounds
    # ax.set_xlim(minx-20, maxx+5)
    # ax.set_ylim(miny-5, maxy)

    base = regions.plot(column='bin', ax=ax[0,0], cmap='viridis', linewidth=0, #inferno_r
        legend=True, antialiased=False)
    # # # imf_countries.plot(ax=base, facecolor="none", edgecolor='grey', linewidth=0.1)
    # # zeros = zeros.plot(ax=base, color='dimgray', edgecolor='dimgray', linewidth=0)
    # # non_imf.plot(ax=base, color='lightgrey', edgecolor='lightgrey', linewidth=0)

    # handles, labels = ax[0,0].get_legend_handles_labels()
    # fig.legend(handles[::-1], labels[::-1])
    # print(fig)
    # # # ctx.add_basemap(ax, crs=regions.crs, source=ctx.providers.CartoDB.Voyager)

    # n = len(regions)
    # name = 'Estimated Carbon Emissions from Universal Mobile Broadband by Sub-National Region (n={})'.format(n)
    # fig.suptitle(name)

    fig.tight_layout()
    fig.savefig(path, dpi=600)

    plt.close(fig)


if __name__ == "__main__":

    countries = find_country_list([])

    # imf_countries = get_country_outlines(countries)
    # non_imf = get_non_imf_outlines(countries)

    # deciles = collect_deciles(countries)#[:300]
    # # out = pd.DataFrame(deciles)
    # # out.to_csv(os.path.join(VIS, '..', 'data.csv'))

    # regions = get_regional_shapes()#[:1000]
    # regions = combine_data(deciles, regions)
    # # regions = pd.DataFrame(regions)
    # # # regions = regions[['GID_id', 'cost', 'decile']]
    # # # regions.to_csv(os.path.join(VIS, '..', 'test.csv'))

    regions = gpd.read_file(os.path.join(VIS,'..','data','test3.shp'), crs='epsg:4326')#[:100]

    path = os.path.join(VIS, 'regions_by_emissions.tif')
    plot_regions_by_emissions(regions, path)#, imf_countries, non_imf)








    # regions = gpd.read_file(os.path.join(VIS,'..','data','test3.shp'), crs='epsg:4326')#[:100]
    # regions = regions[regions['iso3'] == 'USA']

    # sns.set(font_scale=0.9)
    # fig, (ax1, ax2, ax3) = plt.subplots(3, figsize=(7, 9))
    # minx, miny, maxx, maxy = regions.total_bounds
    # ax1.set_aspect('auto')
    # ax1.set_xlim(xmin=-130, xmax=-50)
    # ax2.set_xlim(xmin=-130, xmax=-50)
    # ax3.set_xlim(xmin=-130, xmax=-50)
    # ax1.set_ylim(ymin=25, ymax=50)
    # ax2.set_ylim(ymin=25, ymax=50)
    # ax3.set_ylim(ymin=25, ymax=50)

    # bins = [0,5,10,15,20,25,30,35,40,45,1e12]
    # labels = [
    #     '<5t $CO_2$',
    #     '<10t $CO_2$',
    #     '<15t $CO_2$',
    #     '<20t $CO_2$',
    #     '<25t $CO_2$',
    #     '<30t $CO_2$',
    #     '<35t $CO_2$',
    #     '<40t $CO_2$',
    #     '<45t $CO_2$',
    #     '>45t $CO_2$'
    # ]
    # regions['bin'] = pd.cut(
    #     regions['emissions_'],
    #     bins=bins,
    #     labels=labels
    # )
    
    # base = regions.plot(
    #     column='bin', 
    #     ax=ax1, 
    #     cmap='viridis', 
    #     linewidth=0.1, #fontsize=8,
    #     edgecolor='grey', 
    #     legend=True,
    #     legend_kwds={
    #         "title": "Emissions (xx/x)", 'title_fontsize': 7,
    #         "loc": "lower right", 
    #         'fontsize': 6, "fancybox":True
    #         } 
    #     )
    # base = regions.plot(
    #     column='bin', 
    #     ax=ax2, 
    #     cmap='viridis', 
    #     linewidth=0.1, #fontsize=8,
    #     edgecolor='grey', 
    #     legend=True,
    #     legend_kwds={
    #         "title": "Emissions (xx/x)", 'title_fontsize': 7,
    #         "loc": "lower right", 
    #         'fontsize': 6, "fancybox":True
    #         } 
    #     )   
    # base = regions.plot(
    #     column='bin', 
    #     ax=ax3, 
    #     cmap='viridis', 
    #     linewidth=0.1, #fontsize=8,
    #     edgecolor='grey', 
    #     legend=True,
    #     legend_kwds={
    #         "title": "Emissions (xx/x)", 'title_fontsize': 7,
    #         "loc": "lower right", 
    #         'fontsize': 6, "fancybox":True
    #         } 
    #     )
    # len = len(regions)
    # t = 'Estimated impacts by US sub-national region (n={})'.format(len)
    # fig.suptitle(t)

    # ax1.set_title('(A) Aggregate existing emissions by US sub-national region', loc='left')
    # ax2.set_title('(B) Aggregate new emissions by US sub-national region', loc='left')
    # ax3.set_title('(C) Per smartphone new emissions by US sub-national region', loc='left')

    # ax1.tick_params(axis='both', which='both', labelsize=7)
    # ax2.tick_params(axis='both', which='both', labelsize=7)
    # ax3.tick_params(axis='both', which='both', labelsize=7)

    # fig.tight_layout()
    # path = os.path.join(VIS, 'demo_usa.png')
    # fig.savefig(path, dpi=300)
