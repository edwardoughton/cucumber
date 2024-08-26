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

        # if not country['iso3'] == 'AFG':
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

            existing_emissions_per_smartphone_t = country_results[item['decile']][0]
            new_emissions_per_smartphone_t = country_results[item['decile']][1]
            total_emissions_per_smartphone_t = country_results[item['decile']][2]

            penetration_rate = 1
            existing_emissions = (
                (item['population'] * penetration_rate) * 
                existing_emissions_per_smartphone_t)
            new_emissions = (
                (item['population'] * penetration_rate) * 
                new_emissions_per_smartphone_t)
            total_emissions = (
                (item['population'] * penetration_rate) * 
                total_emissions_per_smartphone_t)

            output.append({
                # 'GID_0': item['GID_0'],
                'GID_id': item['GID_id'],
                # 'GID_level': item['GID_level'],
                'population': item['population'],
                'area_km2': item['area_km2'],
                'pop_density_km2': item['population'] / item['area_km2'],
                'existing_emissions_t': existing_emissions,
                'new_emissions_t': new_emissions,
                'total_emissions_t': total_emissions,
                'decile': item['decile'],
            })

    output = pd.DataFrame(output)
    output.to_csv(path_out, index=False)

    return output


def collect_results(countries):
    """
    Collect results.

    """
    output = {}

    for country in countries:

        # if not country['iso3'] == 'AFG':
        #     continue

        interim = {}

        filename = "results_{}.csv".format(country['iso3'])
        folder = os.path.join(RESULTS, 'model_results', country['iso3'])
        path = os.path.join(folder, filename)
        data = pd.read_csv(path)

        data = data[data['capacity'] == 30]
        data = data[data['generation'] == '4G']
        data = data[data['backhaul'] == 'wireless']
        data = data[data['energy_scenario'] == 'aps-2030']      

        data['existing_emissions_per_smartphone_t'] = (
            ((data['total_existing_emissions_t_co2']) * 1e3) /
            data['population_with_smartphones']
        )

        data['new_emissions_per_smartphone_t'] = (
            ((data['total_new_emissions_t_co2']) * 1e3) /
            data['population_with_smartphones']
        )

        data['total_emissions_per_smartphone_t'] = (
            ((data['total_existing_emissions_t_co2'] + 
            data['total_new_emissions_t_co2']) * 1e3) /
            data['population_with_smartphones']
        )
        data = data[[
            'decile',
            'existing_emissions_per_smartphone_t',
            'new_emissions_per_smartphone_t',
            'total_emissions_per_smartphone_t'
            ]]
        data = data.to_dict('records')

        for item in data:

            interim[item['decile']] = (
                item['existing_emissions_per_smartphone_t'], #existing
                item['new_emissions_per_smartphone_t'], #new
                item['total_emissions_per_smartphone_t'] #total
                )

        output[country['iso3']] = interim

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
    # regions = regions[regions['iso3'] == 'CAN']
    regions = regions[['GID_id', 'iso3', 'geometry']] #[:1000]
    regions = regions.copy()
    regions = regions.merge(deciles, how='left', left_on='GID_id', right_on='GID_id')
    regions.reset_index(drop=True, inplace=True)
    regions.to_file(os.path.join(VIS,'..','data','test3.shp'))

    return regions


def plot_panel(regions):
    """
    Plot emissions panel. 
    
    """
    sns.set(font_scale=0.9)
    fig, (ax1, ax2, ax3) = plt.subplots(3, figsize=(7, 9), layout='constrained')

    bins = [-10,1,25,50,75,100,150,250,500,750,1e12]
    labels = [
        '<1t $CO_2$',
        '<25t $CO_2$',
        '<50t $CO_2$',
        '<75t $CO_2$',
        '<100t $CO_2$',
        '<150t $CO_2$',
        '<250t $CO_2$',
        '<500t $CO_2$',
        '<750t $CO_2$',
        '>750t $CO_2$'
    ]

    #plot1
    regions['bin1'] = pd.cut(
        regions['existing_e'] / 1e3, #convert kg to t
        bins=bins,
        labels=labels
    )
    base = regions.plot(
        column='bin1', 
        ax=ax1, 
        cmap='viridis', 
        linewidth=0, #fontsize=8,
        legend=True,
        legend_kwds={
            # "title": "Emissions (xx/x)", 
            'title_fontsize': 7,
            "loc": "lower left", 
            'fontsize': 6, "fancybox":True
            } 
        )

    #plot2
    regions['bin2'] = pd.cut(
        regions['new_emissi'] / 1e3, # convert kg to t
        bins=bins,
        labels=labels
    )
    base = regions.plot(
        column='bin2', 
        ax=ax2, 
        cmap='viridis', 
        linewidth=0, #fontsize=8,
        legend=True,
        legend_kwds={
            # "title": "Emissions (xx/x)", 
            'title_fontsize': 7,
            "loc": "lower left", 
            'fontsize': 6, "fancybox":True
            } 
        )   
    
    #plot3
    regions['bin3'] = pd.cut(
        regions['total_emis'] / 1e3, # convert kg to t
        bins=bins,
        labels=labels
    )
    base = regions.plot(
        column='bin3', 
        ax=ax3, 
        cmap='viridis', 
        linewidth=0, #fontsize=8,
        legend=True,
        legend_kwds={
            # "title": "Emissions (xx/x)", 
            'title_fontsize': 7,
            "loc": "lower left", 
            'fontsize': 6, "fancybox":True
            } 
        )   

    t = 'Reaching Global Universal Mobile Broadband (n={})'.format(len(regions))
    fig.suptitle(t)

    ax1.set_title('(A) Emissions from existing mobile infrastructure by sub-national region', loc='left')
    ax2.set_title('(B) New emissions by sub-national region (30 GB/Month/Smartphone)', loc='left')
    ax3.set_title('(C) Total emissions by sub-national region (30 GB/Month/Smartphone)', loc='left')

    ax1.tick_params(axis='both', which='both', labelsize=7)
    ax2.tick_params(axis='both', which='both', labelsize=7)
    ax3.tick_params(axis='both', which='both', labelsize=7)

    fig.tight_layout()
    path = os.path.join(VIS, 'demo.png')
    fig.savefig(path, dpi=300)


if __name__ == "__main__":

    countries = find_country_list([])

    deciles = collect_deciles(countries)#[:300]

    regions = get_regional_shapes()#[:1000]
    regions = combine_data(deciles, regions)

    path_in = os.path.join(VIS,'..','data','test3.shp')
    regions = gpd.read_file(path_in, crs='epsg:4326')#[:100]

    plot_panel(regions)


