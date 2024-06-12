"""
Caclulate new revised outputs.

Written by Ed Oughton.

June 7th 2024.

"""
import os
import csv
import configparser
import pandas as pd
import geopandas
from collections import OrderedDict
from tqdm import tqdm

from cuba.demand import estimate_demand
from cuba.supply import estimate_supply
from cuba.energy import assess_energy
from cuba.emissions import assess_emissions
from cuba.costs import assess_cost

from options import ENERGY_DEMAND, EMISSIONS_FACTORS, generate_tech_options
from misc import find_country_list

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, '..', '..', 'data_raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')
OUTPUT = os.path.join(BASE_PATH, '..', 'results', 'model_results')


def read_capacity_lut(path):
    """

    """
    capacity_lut = {}

    with open(path, 'r') as capacity_lookup_file:
        reader = csv.DictReader(capacity_lookup_file)
        for idx, row in enumerate(reader):

            if float(row["capacity_mbps_km2"]) <= 0:
                continue

            environment = row["environment"].lower()
            ant_type = row["ant_type"]
            frequency_GHz = str(int(float(row["frequency_GHz"]) * 1e3))
            generation = str(row["generation"])
            ci = str(row['confidence_interval'])

            if (ant_type, frequency_GHz, generation, ci) \
                not in capacity_lut:
                capacity_lut[(ant_type, frequency_GHz, generation, ci)
                    ] = []

            capacity_lut[(
                ant_type,
                frequency_GHz,
                generation,
                ci)].append((
                    float(row["sites_per_km2"]),
                    float(row["capacity_mbps_km2"])
                ))

        for key, value_list in capacity_lut.items():
            value_list.sort(key=lambda tup: tup[0])

    return capacity_lut


def load_on_grid_mix(country, energy_scenario, path):
    """
    Load IEA WEO2023 data.
    
    """
    iea_classification = country['iea_classification']

    if energy_scenario == 'sps-2022':
        energy_scenario_long = "Stated Policies Scenario"
        year = 2022
    if energy_scenario == 'sps-2030':
        energy_scenario_long = "Stated Policies Scenario"
        year = 2030
    if energy_scenario == 'aps-2030':
        energy_scenario_long = "Announced Pledges Scenario"
        year = 2030
    
    on_grid_mix = {}

    data = pd.read_csv(path)
    data = data[data.FLOW == 'Electricity generation']
    data = data[data.SCENARIO == energy_scenario_long]
    data = data[data.YEAR == int(year)]
    data = data[data.PRODUCT != 'Total']
    data = data[data.REGION != 'World']
    data = data[['PRODUCT','REGION','VALUE']]

    #calculate energy generation mix share
    data['share']  = (
        data['VALUE'] / 
        data.groupby('REGION')['VALUE'].transform('sum')
    )
    # data.to_csv(os.path.join(BASE_PATH,'test.csv'), index=False)

    for idx, item in data.iterrows():
        
        if not item['REGION'] == iea_classification:
            continue

        on_grid_mix[item['PRODUCT']] = item['share']

    return on_grid_mix


def collect_results(countries):
    """
    
    """
    output = []

    for country in countries:

        iso3 = country['iso3']
        filename = 'results_{}.csv'.format(iso3)
        path = os.path.join(OUTPUT, iso3, filename)
        data = pd.read_csv(path)
        data = data.to_dict('records')
        output = output + data
    
    output = pd.DataFrame(output)
    filename = 'global_results.csv'.format(iso3)
    path_out = os.path.join(OUTPUT, '..', 'global_results', filename)
    output.to_csv(path_out, index=False)

    return


if __name__ == '__main__':

    countries = find_country_list([])
    options = generate_tech_options()

    if not os.path.exists(OUTPUT):
        os.makedirs(OUTPUT)

    path = os.path.join(DATA_INTERMEDIATE, 'luts', 'capacity_lut_by_frequency.csv')
    capacity_lut = read_capacity_lut(path)

    for country in tqdm(countries):#[::-1]:#[:1]:

        iso3 = country['iso3']

        # if not iso3 == "GBR":
        #     continue

        OUTPUT_COUNTRY = os.path.join(OUTPUT, iso3)

        if not os.path.exists(OUTPUT_COUNTRY):
            os.makedirs(OUTPUT_COUNTRY)

        output = []

        for option in options:
            
            folder = os.path.join(DATA_RAW, 'iea_data')
            filename = 'WEO2023_AnnexA_Free_Dataset_Regions.csv'
            path_in = os.path.join(folder, filename)
            energy_scenario = option.split('_')[3]
            on_grid_mix = load_on_grid_mix(country, energy_scenario, path_in)

            print('--Working on {}: {}'.format(iso3, option))

            filename = 'decile_data.csv'
            path_out = os.path.join(DATA_INTERMEDIATE, country['iso3'], filename)
            deciles = pd.read_csv(path_out)#[:1]
            # capacity_generation_backhaul_energy_year
            deciles['capacity'] = option.split('_')[0]
            deciles['generation'] = option.split('_')[1]
            deciles['backhaul'] = option.split('_')[2]
            deciles['energy_scenario'] = option.split('_')[3]
            # deciles['year'] = option.split('_')[4]

            deciles = deciles.to_dict('records')#[:1]

            deciles = estimate_demand(
                country,
                deciles,
            )

            deciles = estimate_supply(
                country,
                deciles,
                capacity_lut,
            )

            deciles = assess_energy(
                country,
                deciles,
            )

            data_emissions = assess_emissions(
                country,
                deciles,
                on_grid_mix,
                EMISSIONS_FACTORS
            )
            
            deciles = assess_cost(
                country,
                deciles,
            )

            output = output + deciles

        output = pd.DataFrame(output)
        filename = 'results_{}.csv'.format(iso3)
        path_out = os.path.join(OUTPUT_COUNTRY, filename)
        output.to_csv(path_out, index=False)

    collect_results(countries)