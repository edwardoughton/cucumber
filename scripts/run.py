"""
Generate data for modeling.

Written by Ed Oughton.

Winter 2020

"""
import os
import csv
import configparser
import pandas as pd
import geopandas
from collections import OrderedDict
from tqdm import tqdm

from options import (OPTIONS, GLOBAL_PARAMETERS, COSTS, INFRA_SHARING_ASSETS,
    COST_TYPES, ENERGY_DEMAND, TECH_LUT)
from cuba.demand import estimate_demand
from cuba.supply import estimate_supply
from cuba.assess import assess
from cuba.energy import assess_energy
from cuba.emissions import assess_emissions
from write import (write_demand, write_results, write_inputs, #define_deciles,
    write_assets, write_energy, write_energy_aggregated, write_energy_annual_aggregated,
    write_emissions, write_emissions_aggregated,
    write_emissions_annual_aggregated, write_power_emissions)
# from countries import COUNTRY_LIST, COUNTRY_PARAMETERS
from misc import find_country_list
from percentages import generate_percentages
from collect_results import collect_results

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')
OUTPUT = os.path.join(BASE_PATH, '..', 'results', 'model_results')


def read_capacity_lut(path):
    """

    """
    capacity_lut = {}

    with open(path, 'r') as capacity_lookup_file:
        reader = csv.DictReader(capacity_lookup_file)
        for row in reader:

            if float(row["capacity_mbps_km2"]) <= 0:
                continue
            environment = row["environment"].lower()
            ant_type = row["ant_type"]
            frequency_GHz = str(int(float(row["frequency_GHz"]) * 1e3))
            generation = str(row["generation"])
            ci = str(row['confidence_interval'])

            if (environment, ant_type, frequency_GHz, generation, ci) \
                not in capacity_lut:
                capacity_lut[(
                    environment, ant_type, frequency_GHz, generation, ci)
                    ] = []

            capacity_lut[(
                environment,
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


def load_penetration(scenario, path):
    """
    Load penetration forecast.

    """
    output = {}

    with open(path, 'r') as source:
        reader = csv.DictReader(source)
        for row in reader:
            if row['scenario'] == scenario.split('_')[0]:
                output[int(row['year'])] = round(float(row['penetration']), 1)

    return output


def load_smartphones(scenario, path):
    """
    Load phone types forecast. The function either uses the specific data
    for the country being modeled, or data from another country in the same
    cluster. If no data are present for the country of the cluster, it
    defaults to the mean values across all surveyed countries.

    """
    output = {}

    settlement_types = [
            'urban',
            'rural'
        ]

    for settlement_type in settlement_types:
        with open(path, 'r') as source:
            reader = csv.DictReader(source)
            intermediate = {}
            for row in reader:
                if row['scenario'] == scenario.split('_')[0]:
                    if settlement_type == row['settlement_type']:
                        intermediate[int(row['year'])] = round(float(row['penetration']), 1)
            output[settlement_type] = intermediate

    return output



def load_country_parameters():
    """

    """
    output = {}

    path = os.path.join(DATA_RAW, 'country_parameters.csv')
    data = pd.read_csv(path, encoding="ISO-8859-1")
    data = data.to_dict('records')

    for item in data:

        iso3 = item['iso3']

        networks = {}
        arpu = {}
        financials = {}

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
            elif 'arpu' in key:
                arpu[key] = value
            else:
                financials[key] = value

        output[iso3] = {
            'networks': networks,
            'arpu': arpu,
            'financials': financials
        }

    return output


def load_core_lut(path):
    """
    """
    interim = []

    with open(path, 'r') as source:
        reader = csv.DictReader(source)
        for row in reader:
            interim.append({
                'GID_id': row['GID_id'],
                'asset': row['asset'],
                'source': row['source'],
                'value': int(round(float(row['value']))),
            })

    asset_types = [
        'core_edge',
        'core_node',
        'regional_edge',
        'regional_node'
    ]

    output = {}

    for asset_type in asset_types:
        asset_dict = {}
        for row in interim:
            if asset_type == row['asset']:
                combined_key = '{}_{}'.format(row['GID_id'], row['source'])
                asset_dict[combined_key] = row['value']
                output[asset_type] = asset_dict

    return output


def country_specific_emissions_factors(country, TECH_LUT):
    """

    """
    iso3 = country['iso3']

    path = os.path.join(DATA_RAW, 'Emissions', 'owid-co2-data_full.csv')
    data = pd.read_csv(path, encoding="ISO-8859-1")

    row = data.loc[data['iso3'] == iso3] #.value[0]
    selected_owid_2019 = row['selected_owid_2019'].values[0]

    lut = {}

    for key1, value1 in TECH_LUT.items():

        interim = {}

        if key1 == 'renewables':
            lut[key1] = value1
            continue

        for key2, value2 in value1.items():

            if key2 == 'carbon_per_kWh':
                interim[key2] = float(selected_owid_2019)
            else:
                interim[key2] = value2

        lut[key1] = interim

    return lut


def load_on_grid_mix(country, path):

    iea_classification = country['iea_classification']

    on_grid_mix = {}

    data = pd.read_csv(path)
    years = data['year'].unique()

    for year in years:
        year_data = {}
        for idx, item in data.iterrows():
            if not item['region'] == iea_classification:
                continue
            if year == item['year']:
                year_data[item['type']] = item['share']

        on_grid_mix[year] = year_data

    return on_grid_mix


def allocate_deciles(data):
    """
    Convert to pandas df, define deciles, and then return as a list of dicts.

    """
    data = pd.DataFrame(data)

    data = define_deciles(data)

    data = data.to_dict('records')

    return data


if __name__ == '__main__':

    countries = find_country_list([])

    if not os.path.exists(OUTPUT):
        os.makedirs(OUTPUT)

    BASE_YEAR = 2020
    END_YEAR = 2030
    TIMESTEP_INCREMENT = 1
    TIMESTEPS = [t for t in range(BASE_YEAR, END_YEAR + 1, TIMESTEP_INCREMENT)]

    path = os.path.join(DATA_RAW, 'pysim5g', 'capacity_lut_by_frequency.csv')
    capacity_lut = read_capacity_lut(path)

    country_parameter_lut = load_country_parameters()

    decision_options = [
        'technology_options',
        # 'business_model_options',
        # 'policy_options',
        # 'power_options',
        # 'business_model_power_options',
    ]

    all_results = []

    for decision_option in decision_options:

        # print('Working on {}'.format(decision_option))

        options = OPTIONS[decision_option]#[:1]

        failures = []

        for country in tqdm(countries):#[::-1]:#[:1]:

            # try:
            regional_annual_demand = []
            regional_results = []
            regional_cost_structure = []
            all_assets = []
            regional_energy_demand = []
            regional_emissions = []

            iso3 = country['iso3']

            OUTPUT_COUNTRY = os.path.join(OUTPUT, iso3)

            if not os.path.exists(OUTPUT_COUNTRY):
                os.makedirs(OUTPUT_COUNTRY)

            if not iso3 == 'BRA':
                continue

            # print('-Working on {}'.format(iso3))

            country_parameters = country_parameter_lut[iso3]

            tech_lut = country_specific_emissions_factors(country, TECH_LUT)

            folder = os.path.join(DATA_RAW, 'iea_data')
            filename = 'iea_forecast.csv'
            on_grid_mix = load_on_grid_mix(country, os.path.join(folder, filename))

            print('--Working on {} in {}'.format(decision_option, iso3))

            for option in options:

                print('Working on {} and {}'.format(option['scenario'], option['strategy']))

                # filename = 'national_market_cost_results_{}.csv'.format(decision_option)
                # path_out = os.path.join(OUTPUT_COUNTRY, filename)
                # if os.path.exists(path_out):
                #     continue

                confidence_intervals = GLOBAL_PARAMETERS['confidence']

                folder = os.path.join(DATA_INTERMEDIATE, iso3, 'subscriptions')
                filename = 'subs_forecast.csv'
                path = os.path.join(folder, filename)
                penetration_lut = load_penetration(option['scenario'], path)

                folder = os.path.join(DATA_INTERMEDIATE, iso3, 'subscriptions')
                filename = 'smartphone_forecast.csv'
                path = os.path.join(folder, filename)
                smartphone_lut = load_smartphones(option['scenario'], path)

                for ci in confidence_intervals:

                    # print('CI: {}'.format(ci))
                    filename = 'decile_data.csv'
                    path_out = os.path.join(DATA_INTERMEDIATE, country['iso3'], filename)
                    data_initial = pd.read_csv(path_out)#[:1]
                    data_initial = data_initial.to_dict('records')

                    data_demand, annual_demand = estimate_demand(
                        country_parameters,
                        data_initial,
                        option,
                        GLOBAL_PARAMETERS,
                        TIMESTEPS,
                        penetration_lut,
                        smartphone_lut
                    )

                    data_supply, assets = estimate_supply(
                        country,
                        data_demand,
                        capacity_lut,
                        option,
                        GLOBAL_PARAMETERS,
                        country_parameters,
                        COSTS,
                        ci,
                        INFRA_SHARING_ASSETS,
                        COST_TYPES
                    )

                    data_assess = assess(
                        country,
                        data_supply,
                        option,
                        GLOBAL_PARAMETERS,
                        country_parameters,
                        TIMESTEPS
                    )

                    data_energy = assess_energy(
                        country,
                        data_assess,
                        assets,
                        option,
                        GLOBAL_PARAMETERS,
                        country_parameters,
                        TIMESTEPS,
                        ENERGY_DEMAND,
                    )

                    data_emissions = assess_emissions(
                        data_energy,
                        tech_lut,
                        on_grid_mix,
                        TIMESTEPS,
                        option,
                        country_parameters
                    )

                    # final_results = allocate_deciles(data_assess)

                    regional_annual_demand = regional_annual_demand + annual_demand
                    regional_results = regional_results + data_assess
                    for key, value in assets.items():
                        all_assets = all_assets + value
                    regional_energy_demand = regional_energy_demand + data_energy
                    regional_emissions = regional_emissions + data_emissions

            all_results = all_results + regional_results

            write_demand(regional_annual_demand, OUTPUT_COUNTRY)

            write_assets(all_assets, OUTPUT_COUNTRY, decision_option)

            write_energy(regional_energy_demand, OUTPUT_COUNTRY, decision_option)

            write_energy_annual_aggregated(regional_energy_demand, regional_annual_demand,
                OUTPUT_COUNTRY, decision_option)

            write_energy_aggregated(regional_energy_demand, regional_annual_demand,
                OUTPUT_COUNTRY, decision_option)

            write_emissions(regional_emissions, OUTPUT_COUNTRY, decision_option)

            write_emissions_annual_aggregated(regional_emissions, regional_annual_demand,
                OUTPUT_COUNTRY, decision_option)

            write_emissions_aggregated(regional_emissions, OUTPUT_COUNTRY,
                decision_option)

            write_power_emissions(regional_emissions, OUTPUT_COUNTRY,
                decision_option)

            write_results(regional_results, OUTPUT_COUNTRY, decision_option)

            write_inputs(OUTPUT_COUNTRY, country, country_parameters,
                            GLOBAL_PARAMETERS, COSTS, decision_option)

            generate_percentages(iso3, decision_option)

        # except:

        #     failures.append(country['iso3'])
        #     print(failures)

        # print(failures)

    # collect_results('national_market_cost_results_technology_options.csv')
    # collect_results('national_market_cost_results_business_model_options.csv')
    # collect_results('national_market_cost_results_policy_options.csv')
    # collect_results('emissions_technology_options.csv')
    # collect_results('power_emissions_power_options.csv')
    # collect_results('emissions_national_business_model_power_options.csv')

    # # write_results(all_results, OUTPUT, 'all_options_all_countries')

    # # print('Completed model run')
