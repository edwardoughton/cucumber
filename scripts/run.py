"""
Compute outputs.

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

from cucumber.demand import estimate_demand
from cucumber.supply import estimate_supply
from cucumber.energy import assess_energy
from cucumber.emissions import assess_emissions
from cucumber.costs import assess_cost

from options import all_options, PARAMETERS
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


def read_emissions_lut(path):
    """

    """
    capacity_lut = {}

    data = pd.read_csv(path)
    regions = data['region'].unique()
    scenarios = data['scenario'].unique()
    data = data.to_dict('records')

    for region in regions:
        
        # if region == 'na'
        region_dict = {}
        for scenario in scenarios:
            technologies = {}
            for item in data:
                if not region == item['region']:
                    continue
                if not scenario == item['scenario']:
                    continue
                technologies[item['generation_twh'].lower()] = item['co2_g_kwh']

            region_dict[scenario] = technologies
        capacity_lut[region] = region_dict

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
    data = data[data.CATEGORY == 'Energy']
    data = data[data.SCENARIO == energy_scenario_long]
    data = data[data.YEAR == int(year)]
    data = data[data.PRODUCT != 'Total']
    data = data[data.REGION != 'World']
    data = data[['PRODUCT','REGION','VALUE']]
    data = data[data['PRODUCT'] != 'Renewables']

    #calculate energy generation mix share
    data['share']  = (
        data['VALUE'] / 
        data.groupby('REGION')['VALUE'].transform('sum')
    )
    # data.to_csv(os.path.join(BASE_PATH,'test.csv'), index=False)

    for idx, item in data.iterrows():

        if not item['REGION'] == iea_classification:
            continue

        product = item['PRODUCT'].lower()
        if product == 'modern bioenergy and renewable waste':
            product = 'bioenergy'
        elif product == 'hydrogen and h2-based fuels':
            product = 'hydrogen and ammonia'
        elif product == 'fossil fuels: with ccus':
            product = 'fossil fuels with ccus'
        elif product == 'coal: unabated':
            product = 'unabated coal'
        elif product == 'natural gas: unabated':
            product = 'unabated natural gas'

        on_grid_mix[product] = item['share'] #* 100

    return on_grid_mix


def load_country_parameters():
    """

    """
    output = {}

    path = os.path.join(BASE_PATH, 'country_parameters.csv')
    data = pd.read_csv(path, encoding="ISO-8859-1")
    data = data.to_dict('records')

    for item in data:

        iso3 = item['iso3']

        networks = {}

        keys = ['urban','suburban','rural']

        for key, value in item.items():

            if 'iso3' in key:
                continue
            if 'country' in key:
                continue
            if 'income' in key:
                continue

            if any(x in key for x in keys):
                networks[key] = value

        output[iso3] = {
            'networks': networks,
        }

    return output


def collect_results(countries):
    """
    
    """
    output = []

    for country in countries:

        if "{}".format(country['adb_region']) == 'nan':
            continue

        iso3 = country['iso3']
        filename = 'results_{}.csv'.format(iso3)
        path = os.path.join(OUTPUT, iso3, filename)
        if not os.path.exists(path):
            print('Path does not exist: {}'.format(path))
        data = pd.read_csv(path)
        data = data.to_dict('records')
        output = output + data
    
    output = pd.DataFrame(output)
    filename = 'global_results.csv'.format(iso3)
    folder = os.path.join(OUTPUT, '..', 'global_results')
    if not os.path.exists(folder):
        os.mkdir(folder)
    path_out = os.path.join(folder, filename)
    output.to_csv(path_out, index=False)

    output = output[[
        'GID_0','decile',
        'capacity','generation',
        'backhaul','energy_scenario','sharing_scenario',
        'income', 'wb_region','adb_region',#'product',
        'population_with_smartphones','smartphones_on_network',
        'demand_mbps_km2',
        'network_required_sites', 
        'network_existing_sites',
        'network_upgraded_sites','network_new_sites',
        'total_upgraded_sites','total_new_sites', 
        'total_cost_equipment_usd',
        'total_cost_backhaul_usd',
        'total_cost_site_build_usd',
        'total_cost_installation_usd',
        'total_cost_operation_and_maintenance_usd',
        'total_cost_power_usd',
        'total_new_cost_usd'
        ]]

    filename = 'global_cost_results.csv'.format(iso3)
    folder = os.path.join(OUTPUT, '..', 'global_results')
    path_out = os.path.join(folder, filename)
    output.to_csv(path_out, index=False)

    return


def collect_satellite_areas(countries):
    """
        
    """
    output = []

    for country in countries:

        if "{}".format(country['adb_region']) == 'nan':
            continue

        iso3 = country['iso3']
        filename = 'regional_data_deciles.csv'
        path = os.path.join(DATA_INTERMEDIATE, iso3, 'population',filename)
        if not os.path.exists(path):
            print('Path does not exist: {}'.format(path))
        data = pd.read_csv(path)
        data = data.to_dict('records')
        output = output + data
    
    output = pd.DataFrame(output)
    filename = 'satellite_areas.csv'.format(iso3)
    folder = os.path.join(OUTPUT, '..', 'global_results')
    if not os.path.exists(folder):
        os.mkdir(folder)
    path_out = os.path.join(folder, filename)
    output.to_csv(path_out, index=False)

    return


if __name__ == '__main__':

    countries = find_country_list([])
    options = all_options()

    if not os.path.exists(OUTPUT):
        os.makedirs(OUTPUT)

    path = os.path.join(DATA_INTERMEDIATE, 'luts', 'capacity_lut_by_frequency.csv')
    capacity_lut = read_capacity_lut(path)

    country_parameters = load_country_parameters()

    filename = 'iea_electricity_emissions_factors.csv'
    folder = os.path.join(DATA_RAW, 'IEA_data', 'WEO2023 extended data')
    path = os.path.join(folder, filename)
    emissions_lut = read_emissions_lut(path)

    for country in tqdm(countries):#[::-1]:#[:1]:

        if "{}".format(country['adb_region']) == 'nan':
            continue
        
        iso3 = country['iso3']
        country.update(PARAMETERS)
        country['networks'] = country_parameters[country['iso3']]['networks']

        # if not iso3 == "KOR":
        #     continue

        print('--Working on {}'.format(iso3))
        
        OUTPUT_COUNTRY = os.path.join(OUTPUT, iso3)

        if not os.path.exists(OUTPUT_COUNTRY):
            os.makedirs(OUTPUT_COUNTRY)

        output = []
        energy_output = []
        emissions_output = []

        for option in options:

            folder = os.path.join(DATA_RAW, 'IEA_data', 'WEO2023 extended data')
            filename = 'WEO2023_Extended_Data_Regions.csv'
            path_in = os.path.join(folder, filename)
            energy_scenario = option.split('_')[3]
            on_grid_mix = load_on_grid_mix(country, energy_scenario, path_in)

            filename = 'decile_data.csv'
            path_out = os.path.join(DATA_INTERMEDIATE, country['iso3'], filename)
            deciles = pd.read_csv(path_out)#[:1]

            # capacity_generation_backhaul_energy_year
            deciles['capacity'] = option.split('_')[0]
            deciles['generation'] = option.split('_')[1]
            deciles['backhaul'] = option.split('_')[2]
            deciles['energy_scenario'] = option.split('_')[3]
            deciles['sharing_scenario'] = option.split('_')[4]
            # deciles = deciles[deciles['decile'] == 7]

            deciles = deciles.to_dict('records')#[9:10]

            deciles = estimate_demand(
                country,
                deciles,
            )

            deciles = estimate_supply(
                country,
                deciles,
                capacity_lut,
            )

            deciles, energy = assess_energy(
                country,
                deciles,
                on_grid_mix
            )

            deciles, emissions = assess_emissions(
                country,
                deciles,
                on_grid_mix,
                emissions_lut
            )

            deciles = assess_cost(
                country,
                deciles,
            )
            
            output = output + deciles
            energy_output = energy_output + energy
            emissions_output = emissions_output + emissions

        output = pd.DataFrame(output)
        if len(output) == 0:
            continue
        filename = 'results_{}.csv'.format(iso3)
        path_out = os.path.join(OUTPUT_COUNTRY, filename)
        output.to_csv(path_out, index=False)

        output = output[[
            'GID_0','decile',
            'capacity','generation',
            'backhaul','energy_scenario','sharing_scenario',
            # 'income','wb_region','iea_classification',#'product',
            'population_total', 'area_km2', 'population_km2',
            'population_with_smartphones','smartphones_on_network',
            'demand_mbps_km2',
            'network_required_sites', 
            'network_existing_sites',
            'network_upgraded_sites','network_new_sites',
            'backhaul_existing','backhaul_new',
            'total_upgraded_sites','total_new_sites', 
            # 'network_existing_energy_kwh','network_new_energy_kwh',
            'total_existing_energy_kwh','total_new_energy_kwh',
            # 'network_existing_emissions_t_co2','network_new_emissions_t_co2',
            'total_existing_emissions_t_co2', 'total_new_emissions_t_co2',
            'total_new_cost_usd'
            ]]
        filename = 'decile_emissions_{}.csv'.format(iso3)
        path_out = os.path.join(OUTPUT_COUNTRY, filename)
        output.to_csv(path_out, index=False)

        output = output[[
            'GID_0',#'decile',
            'capacity','generation',
            'backhaul','energy_scenario','sharing_scenario',
            #'income', 'wb_region','iea_classification',#'product',
            'population_total', 'area_km2', 'population_km2',
            'population_with_smartphones','smartphones_on_network',
            'demand_mbps_km2',
            'network_required_sites', 
            'network_existing_sites',
            'network_upgraded_sites','network_new_sites',
            'backhaul_existing','backhaul_new',
            'total_upgraded_sites','total_new_sites', 
            # 'network_existing_energy_kwh','network_new_energy_kwh',
            'total_existing_energy_kwh','total_new_energy_kwh',
            # 'network_existing_emissions_t_co2','network_new_emissions_t_co2',
            'total_existing_emissions_t_co2', 'total_new_emissions_t_co2',
            'total_new_cost_usd'
            ]]
        output = output.groupby([
            'GID_0','capacity','generation',
            'backhaul','energy_scenario','sharing_scenario'], as_index=False).sum()
        filename = 'national_emissions_{}.csv'.format(iso3)
        path_out = os.path.join(OUTPUT_COUNTRY, filename)
        output.to_csv(path_out, index=False)

    collect_results(countries)

    collect_satellite_areas(countries)
    