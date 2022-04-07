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

from options import (OPTIONS, GLOBAL_PARAMETERS, COSTS, INFRA_SHARING_ASSETS,
    COST_TYPES, ENERGY_DEMAND, TECH_LUT)
from cuba.demand import estimate_demand
from cuba.supply import estimate_supply
from cuba.assess import assess
from cuba.energy import assess_energy
from cuba.emissions import assess_emissions
from write import (define_deciles, write_demand, write_results, write_inputs,
    write_assets, write_energy, write_emissions, write_emissions_aggregated,
    write_power_emissions)
from countries import COUNTRY_LIST, COUNTRY_PARAMETERS
from percentages import generate_percentages

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

DATA_RAW = os.path.join(BASE_PATH, 'raw')
DATA_INTERMEDIATE = os.path.join(BASE_PATH, 'intermediate')
DATA_PROCESSED = os.path.join(BASE_PATH, 'processed')
OUTPUT = os.path.join(BASE_PATH, '..', 'results', 'model_results')


def load_regions(country, path, sites_lut):
    """
    Load country regions.

    """
    data_initial = []

    regions = pd.read_csv(path)

    regions['geotype'] = regions.apply(define_geotype, axis=1)

    regions = regions.to_dict('records')

    for item in regions:
        for key, value in sites_lut.items():
            if item['GID_id'] == key:
                data_initial.append({
                    'GID_0': item['GID_0'],
                    'GID_id': item['GID_id'],
                    'GID_level': item['GID_level'],
                    'population_total': item['population'],
                    # 'population_over_10': item['population_over_10'],
                    # 'population_f_over_10': item['population_f_over_10'],
                    # 'population_m_over_10': item['population_m_over_10'],
                    'area_km2': item['area_km2'],
                    'population_km2': item['population_km2'],
                    # 'population_over_10yrs_km2': item['population_over_10yrs_km2'],
                    'mean_luminosity_km2': item['mean_luminosity_km2'],
                    'geotype': item['geotype'],
                    'sites_4G': value['sites_4G'],
                    'total_estimated_sites': value['total_estimated_sites'],
                    'backhaul_wireless': value['backhaul_wireless'],
                    'backhaul_fiber': value['backhaul_fiber'],
                    'on_grid_perc': value['on_grid_perc'],
                    'grid_other_perc': value['grid_other_perc'],
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


def lookup_cost(lookup, strategy, environment):
    """
    Find cost of network.

    """
    if (strategy, environment) not in lookup:
        raise KeyError("Combination %s not found in lookup table",
                       (strategy, environment))

    density_capacities = lookup[
        (strategy, environment)
    ]

    return density_capacities


def find_country_list(continent_list):
    """

    """
    path_processed = os.path.join(DATA_INTERMEDIATE,'global_countries.shp')
    countries = geopandas.read_file(path_processed)

    subset = countries.loc[countries['continent'].isin(continent_list)]

    country_list = []
    country_regional_levels = []

    for name in subset.GID_0.unique():

        country_list.append(name)

        if name in ['ESH', 'LBY', 'LSO'] :
            regional_level =  1
        else:
            regional_level = 2

        country_regional_levels.append({
            'country': name,
            'regional_level': regional_level,
        })

    return country_list, country_regional_levels


def load_cluster(path, iso3):
    """
    Load cluster number. You need to make sure the
    R clustering script (podis/vis/clustering/clustering.r)
    has been run first.

    """
    output = {}

    if len(iso3) <= 3:
        with open(path, 'r') as source:
            reader = csv.DictReader(source)
            for row in reader:
                if row['ISO_3digit'] == iso3:
                    output[iso3] = row['cluster']

    if len(iso3) > 3:

        list_of_country_codes = []
        country_codes = iso3.split('-')
        list_of_country_codes.extend(country_codes)

        for item in list_of_country_codes:
            with open(path, 'r') as source:
                reader = csv.DictReader(source)

                for row in reader:
                    if row['ISO_3digit'] == item:
                        output[item] = row['cluster']

    return output


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


def load_sites(country, sites1, sites2):
    """
    Load sites lookup table.

    """
    output = {}

    GID_id = 'GID_{}'.format(country['regional_level'])

    sites1 = pd.read_csv(sites1)
    sites2 = pd.read_csv(sites2)

    for idx, site1 in sites1.iterrows():
        for idx, site2 in sites2.iterrows():
            if site1[GID_id] == site2['GID_id']:
                output[site1[GID_id]] = {
                    'GID_0': site1['GID_0'],
                    # 'sites_2G': int(site1['sites_2G']),
                    # 'sites_3G': int(site1['sites_3G']),
                    'sites_4G': int(site1['sites_4G']),
                    'total_estimated_sites': int(site1['total_estimated_sites']),
                    'backhaul_wireless': float(site1['backhaul_wireless']),
                    'backhaul_fiber':  float(site1['backhaul_fiber']),
                    'on_grid_perc': float(site2['on_grid_perc']),
                    'grid_other_perc': float(site2['grid_other_perc']),
                    'total_sites': site2['total_sites'],
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


def load_on_grid_mix(path):

    on_grid_mix = {}

    data = pd.read_csv(path)
    years = data['year'].unique()

    for year in years:
        year_data = {}
        for idx, item in data.iterrows():
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

    if not os.path.exists(OUTPUT):
        os.makedirs(OUTPUT)

    BASE_YEAR = 2020
    END_YEAR = 2030
    TIMESTEP_INCREMENT = 1
    TIMESTEPS = [t for t in range(BASE_YEAR, END_YEAR + 1, TIMESTEP_INCREMENT)]

    path = os.path.join(DATA_RAW, 'pysim5g', 'capacity_lut_by_frequency.csv')
    capacity_lut = read_capacity_lut(path)

    decision_options = [
        'technology_options',
        'business_model_options',
        'policy_options',
        'power_options',
    ]

    # all_results = []

    for decision_option in decision_options:

        print('Working on {}'.format(decision_option))

        options = OPTIONS[decision_option]

        for country in COUNTRY_LIST:#[:1]:

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

            if not iso3 == 'COL':
                continue

            print('Working on {}'.format(iso3))

            country_parameters = COUNTRY_PARAMETERS[iso3]

            folder = os.path.join(DATA_INTERMEDIATE, iso3, 'sites')
            sites1 = os.path.join(folder, 'sites.csv')
            sites2 = os.path.join(folder, 'site_power', 'b_site_power_lut.csv')
            sites_lut = load_sites(country, sites1, sites2)
            # sites_lut_to_write = pd.DataFrame(sites_lut)

            folder = os.path.join(DATA_INTERMEDIATE, iso3, 'network')
            filename = 'core_lut.csv'
            core_lut = load_core_lut(os.path.join(folder, filename))

            folder = os.path.join(DATA_RAW, 'iea_data')
            filename = 'iea_forecast.csv'
            on_grid_mix = load_on_grid_mix(os.path.join(folder, filename))

            print('-----')
            print('Working on {} in {}'.format(decision_option, iso3))
            print(' ')

            for option in options:

                print('Working on {} and {}'.format(option['scenario'], option['strategy']))

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

                    print('CI: {}'.format(ci))

                    filename = 'regional_data.csv'
                    path = os.path.join(DATA_INTERMEDIATE, iso3, filename)
                    data_initial = load_regions(country, path, sites_lut)#[:20]

                    data_demand, annual_demand = estimate_demand(
                        data_initial,
                        option,
                        GLOBAL_PARAMETERS,
                        country_parameters,
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
                        core_lut,
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
                        TECH_LUT,
                        on_grid_mix,
                        TIMESTEPS,
                        option
                    )

                    final_results = allocate_deciles(data_assess)

                    regional_annual_demand = regional_annual_demand + annual_demand
                    regional_results = regional_results + final_results
                    # all_assets = all_assets + assets
                    regional_energy_demand = regional_energy_demand + data_energy
                    regional_emissions = regional_emissions + data_emissions

            # all_results = all_results + regional_results

            write_demand(regional_annual_demand, OUTPUT_COUNTRY)

            # write_assets(all_assets, OUTPUT_COUNTRY, decision_option)

            write_energy(regional_energy_demand, OUTPUT_COUNTRY, decision_option)

            write_emissions(regional_emissions, OUTPUT_COUNTRY, decision_option)

            write_emissions_aggregated(regional_emissions, OUTPUT_COUNTRY,
                decision_option)

            write_power_emissions(regional_emissions, OUTPUT_COUNTRY,
                decision_option)

            write_results(regional_results, OUTPUT_COUNTRY, decision_option)

            write_inputs(OUTPUT_COUNTRY, country, country_parameters,
                            GLOBAL_PARAMETERS, COSTS, decision_option)

            generate_percentages(iso3, decision_option)

    # write_results(all_results, OUTPUT, 'all_options_all_countries')

    print('Completed model run')
