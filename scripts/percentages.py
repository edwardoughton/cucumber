"""
Estimate the percentage differences across scenarios and strategies.

Written by Ed Oughton.

July 2020

"""
import os
import configparser
import numpy as np
import pandas as pd

from countries import COUNTRY_LIST

CONFIG = configparser.ConfigParser()
CONFIG.read(os.path.join(os.path.dirname(__file__), 'script_config.ini'))
BASE_PATH = CONFIG['file_locations']['base_path']

RESULTS = os.path.join(BASE_PATH, '..', 'results', 'model_results')
OUTPUT = os.path.join(BASE_PATH, '..', 'results', 'percentages')


def generate_percentages(iso3, decision_option):
    """
    Meta function to hold all other function calls.

    """
    if not os.path.exists(os.path.join(OUTPUT)):
        os.makedirs(os.path.join(OUTPUT))

    if decision_option == 'technology_options':

        filename = 'national_market_results_technology_options.csv'
        path = os.path.join(RESULTS, iso3, filename)

        if os.path.exists(path):
            data = pd.read_csv(path)
            data = process_technology_data(data)
            filename = 'percentages_technologies_{}.csv'.format(iso3)
            path = os.path.join(OUTPUT, filename)
            data.to_csv(path, index=False)

    if decision_option == 'business_model_options':

        filename = 'national_market_results_business_model_options.csv'
        path = os.path.join(RESULTS, iso3, filename)

        if os.path.exists(path):

            data = pd.read_csv(path)
            data = process_sharing_data(data)
            filename = 'percentages_sharing_{}.csv'.format(iso3)
            path = os.path.join(OUTPUT, filename)
            data.to_csv(path, index=False)

    if decision_option == 'policy_options':

        filename = 'national_market_results_policy_options.csv'
        path = os.path.join(RESULTS, iso3, filename)

        if os.path.exists(path):

            data = pd.read_csv(path)
            data = process_policy_data(data)
            filename = 'percentages_policy_{}.csv'.format(iso3)
            path = os.path.join(OUTPUT, filename)
            data.to_csv(path, index=False)

    if decision_option == 'mixed_options':
        filename = 'national_market_results_mixed_options.csv'
        path = os.path.join(RESULTS, iso3, filename)

        if os.path.exists(path):

            data = pd.read_csv(path)
            data = process_mixed_data(data)
            filename = 'percentages_mixed_{}.csv'.format(iso3)
            path = os.path.join(OUTPUT, filename)
            data.to_csv(path, index=False)

    if decision_option == 'energy_and_emissions':
        filename = 'emissions_technology_options.csv'
        path = os.path.join(RESULTS, iso3, filename)

        if os.path.exists(path):

            data = pd.read_csv(path)
            data = process_emissions_data(data)
            filename = 'percentages_emissions_{}.csv'.format(iso3)
            path = os.path.join(OUTPUT, filename)
            data.to_csv(path, index=False)



    print('--Finished percentages: {}'.format(decision_option))


def find_scenario_variants(data):
    """


    """
    output = []

    scenarios = set()
    strategies = set()
    confidence_levels = set()

    for idx, item in data.iterrows():
        scenarios.add(item['scenario'])
        strategies.add(item['strategy'])
        confidence_levels.add(item['confidence'])

    for scenario in list(scenarios):
        for strategy in list(strategies):
            for ci in list(confidence_levels):
                output.append(
                    (scenario, strategy, ci)
                )

    return output


def process_technology_data(data):
    """
    Process technology strategies.

    Parameters
    ----------
    data : pandas df
        All model results.

    Returns
    -------
    data : pandas df
        All processed model results.

    """
    data.loc[data['scenario'].str.endswith('5_5_5', na=False), 'capacity'] = '5 Mbps'
    data.loc[data['scenario'].str.endswith('10_10_10', na=False), 'capacity'] = '10 Mbps'
    data.loc[data['scenario'].str.endswith('20_20_20', na=False), 'capacity'] = '20 Mbps'

    data.loc[data['scenario'].str.startswith('low', na=False), 'scenario'] = 'Low'
    data.loc[data['scenario'].str.startswith('baseline', na=False), 'scenario'] = 'Baseline'
    data.loc[data['scenario'].str.startswith('high', na=False), 'scenario'] = 'High'

    data['strategy'] = data['strategy'].replace(['3G_umts_wireless_baseline_baseline_baseline_baseline'], '3G (W)')
    data['strategy'] = data['strategy'].replace(['3G_umts_fiber_baseline_baseline_baseline_baseline'], '3G (FB)')
    data['strategy'] = data['strategy'].replace(['4G_epc_wireless_baseline_baseline_baseline_baseline'], '4G (W)')
    data['strategy'] = data['strategy'].replace(['4G_epc_fiber_baseline_baseline_baseline_baseline'], '4G (FB)')
    data['strategy'] = data['strategy'].replace(['5G_nsa_wireless_baseline_baseline_baseline_baseline'], '5G (W)')
    data['strategy'] = data['strategy'].replace(['5G_nsa_fiber_baseline_baseline_baseline_baseline'], '5G (FB)')

    data['generation'] = data['strategy'].str.split(' ').str[0]
    data['backhaul'] = data['strategy'].str.split(' ').str[1]

    data = data[['scenario', 'capacity', 'generation', 'backhaul',
                'social_cost']].reset_index()

    data_gen = data.copy()
    data_gen['perc_saving_vs_3G'] = round(data_gen.groupby(
                                    ['scenario', 'capacity', 'backhaul'])[
                                    'social_cost'].pct_change()*100)

    data_gen = data_gen.dropna()

    data = pd.merge(data,
            data_gen[['scenario', 'capacity', 'generation', 'backhaul', 'perc_saving_vs_3G']],
            how='left',
            left_on=['scenario', 'capacity', 'generation', 'backhaul'],
            right_on = ['scenario', 'capacity', 'generation', 'backhaul']
        )

    data_backhaul = data[['scenario', 'capacity', 'generation',
        'backhaul', 'social_cost']].copy()

    data_backhaul['w_over_fb'] = round(data_backhaul.groupby(
                                    ['scenario', 'capacity', 'generation'])[
                                    'social_cost'].pct_change()*100)
    data_gen = data_gen.dropna()

    data = pd.merge(data,
            data_backhaul[['scenario', 'capacity', 'generation', 'backhaul', 'w_over_fb']],
            how='left',
            left_on=['scenario', 'capacity', 'generation', 'backhaul'],
            right_on = ['scenario', 'capacity', 'generation', 'backhaul']
        )

    return data


def process_sharing_data(data):
    """
    Process infrastructure sharing strategies.

    Parameters
    ----------
    data : pandas df
        All model results.

    Returns
    -------
    data : pandas df
        All processed model results.

    """
    data.loc[data['scenario'].str.endswith('5_5_5', na=False), 'capacity'] = '5 Mbps'
    data.loc[data['scenario'].str.endswith('10_10_10', na=False), 'capacity'] = '10 Mbps'
    data.loc[data['scenario'].str.endswith('20_20_20', na=False), 'capacity'] = '20 Mbps'

    data.loc[data['scenario'].str.startswith('low', na=False), 'scenario'] = 'Low'
    data.loc[data['scenario'].str.startswith('baseline', na=False), 'scenario'] = 'Baseline'
    data.loc[data['scenario'].str.startswith('high', na=False), 'scenario'] = 'High'

    data['strategy'] = data['strategy'].replace(['4G_epc_wireless_baseline_baseline_baseline_baseline'], 'Baseline')
    data['strategy'] = data['strategy'].replace(['4G_epc_wireless_passive_baseline_baseline_baseline'], 'Passive')
    data['strategy'] = data['strategy'].replace(['4G_epc_wireless_active_baseline_baseline_baseline'], 'Active')
    data['strategy'] = data['strategy'].replace(['4G_epc_wireless_srn_baseline_baseline_baseline'], 'SRN')

    data = data[['scenario', 'capacity', 'strategy', 'social_cost']]

    baseline = data.loc[data['strategy'] == 'Baseline']

    data = pd.merge(data, baseline,
                how='left',
                left_on=['scenario', 'capacity'],
                right_on = ['scenario', 'capacity']
            )

    cost_type_y = 'social_cost' + '_y'
    cost_type_x = 'social_cost' + '_x'
    data['saving_against_baseline'] = ((abs(data[cost_type_y] - data[cost_type_x])) /
                                    data[cost_type_y]) * 100

    data['saving_against_baseline'] = round(data['saving_against_baseline'], 1)

    return data


def process_policy_data(data):
    """
    Process policy strategies.

    Parameters
    ----------
    data : pandas df
        All model results.

    Returns
    -------
    data : pandas df
        All processed model results.

    """
    data.loc[data['scenario'].str.endswith('5_5_5', na=False), 'capacity'] = '5 Mbps'
    data.loc[data['scenario'].str.endswith('10_10_10', na=False), 'capacity'] = '10 Mbps'
    data.loc[data['scenario'].str.endswith('20_20_20', na=False), 'capacity'] = '20 Mbps'

    data.loc[data['scenario'].str.startswith('low', na=False), 'scenario'] = 'Low'
    data.loc[data['scenario'].str.startswith('baseline', na=False), 'scenario'] = 'Baseline'
    data.loc[data['scenario'].str.startswith('high', na=False), 'scenario'] = 'High'

    data['strategy'] = data['strategy'].replace(['4G_epc_wireless_baseline_baseline_low_baseline'], 'Low Spectrum Fees')
    data['strategy'] = data['strategy'].replace(['4G_epc_wireless_baseline_baseline_baseline_baseline'], 'Baseline')
    data['strategy'] = data['strategy'].replace(['4G_epc_wireless_baseline_baseline_high_baseline'], 'High Spectrum Fees')

    data['strategy'] = data['strategy'].replace(['4G_epc_wireless_baseline_baseline_baseline_low'], 'Low Tax')
    data['strategy'] = data['strategy'].replace(['4G_epc_wireless_baseline_baseline_baseline_high'], 'High Tax')

    data = data[['scenario', 'capacity', 'strategy', 'social_cost']]

    baseline = data.loc[data['strategy'] == 'Baseline']

    data = pd.merge(data, baseline,
                how='left',
                left_on=['scenario', 'capacity'],
                right_on = ['scenario', 'capacity']
            )

    cost_type_y = 'social_cost' + '_y'
    cost_type_x = 'social_cost' + '_x'
    data['saving_against_baseline'] = ((abs(data[cost_type_y] - data[cost_type_x])) /
                                    data[cost_type_y]) * 100

    data['saving_against_baseline'] = round(data['saving_against_baseline'], 1)

    return data


def process_mixed_data(data):
    """
    Process mixed strategies.

    Parameters
    ----------
    data : pandas df
        All model results.

    Returns
    -------
    data : pandas df
        All processed model results.

    """
    data.loc[data['scenario'].str.endswith('5_5_5', na=False), 'capacity'] = '5 Mbps'
    data.loc[data['scenario'].str.endswith('10_10_10', na=False), 'capacity'] = '10 Mbps'
    data.loc[data['scenario'].str.endswith('20_20_20', na=False), 'capacity'] = '20 Mbps'

    data.loc[data['scenario'].str.startswith('low', na=False), 'scenario'] = 'Low'
    data.loc[data['scenario'].str.startswith('baseline', na=False), 'scenario'] = 'Baseline'
    data.loc[data['scenario'].str.startswith('high', na=False), 'scenario'] = 'High'

    data = data[data['strategy'].isin([
        '4G_epc_wireless_baseline_baseline_baseline_baseline',
        '4G_epc_wireless_srn_baseline_low_low',
    ])].reset_index()

    data['strategy'] = data['strategy'].replace(['4G_epc_wireless_baseline_baseline_baseline_baseline'], 'Baseline')
    data['strategy'] = data['strategy'].replace(['4G_epc_wireless_srn_baseline_low_low'], '4G (W) Mixed')

    data = data[['scenario', 'capacity', 'strategy', 'social_cost']]

    baseline = data.loc[data['strategy'] == 'Baseline']

    data = pd.merge(data, baseline,
                how='left',
                left_on=['scenario', 'capacity'],
                right_on = ['scenario', 'capacity']
            )

    cost_type_y = 'social_cost' + '_y'
    cost_type_x = 'social_cost' + '_x'
    data['saving_against_baseline'] = ((abs(data[cost_type_y] - data[cost_type_x])) /
                                    data[cost_type_y]) * 100

    data['saving_against_baseline'] = round(data['saving_against_baseline'], 1)

    return data


def process_emissions_data(data):
    """
    Process emissions strategies.

    Parameters
    ----------
    data : pandas df
        All model results.

    Returns
    -------
    data : pandas df
        All processed model results.

    """
    data.loc[data['scenario'].str.endswith('5_5_5', na=False), 'capacity'] = '5 Mbps'
    data.loc[data['scenario'].str.endswith('10_10_10', na=False), 'capacity'] = '10 Mbps'
    data.loc[data['scenario'].str.endswith('20_20_20', na=False), 'capacity'] = '20 Mbps'

    data.loc[data['scenario'].str.startswith('low', na=False), 'scenario'] = 'Low'
    data.loc[data['scenario'].str.startswith('baseline', na=False), 'scenario'] = 'Baseline'
    data.loc[data['scenario'].str.startswith('high', na=False), 'scenario'] = 'High'

    data['strategy'] = data['strategy'].replace(['4G_epc_wireless_baseline_baseline_baseline_baseline'], '4G (W)')
    data['strategy'] = data['strategy'].replace(['4G_epc_fiber_baseline_baseline_baseline_baseline'], '4G (FB)')
    data['strategy'] = data['strategy'].replace(['5G_nsa_wireless_baseline_baseline_baseline_baseline'], '5G (W)')
    data['strategy'] = data['strategy'].replace(['5G_nsa_fiber_baseline_baseline_baseline_baseline'], '5G (FB)')

    data['generation'] = data['strategy'].str.split(' ').str[0]
    data['backhaul'] = data['strategy'].str.split(' ').str[1]

    data = data[['capacity', 'strategy', 'scenario', 'generation', 'backhaul',
        'total_annual_energy_demand_kwh',
        'demand_carbon_per_kwh', 'nitrogen_oxide_per_kwh',
        'sulpher_dioxide_per_kwh', 'pm10_per_kwh'
        ]]

    data = data.groupby([
        'capacity', 'strategy', 'scenario',
        'generation', 'backhaul']).sum().reset_index()

    data_gen = data.copy()
    data_gen['perc_energy_dif_vs_4G'] = round(data_gen.groupby(
                                    ['capacity', 'scenario', 'backhaul'])[
                                    'total_annual_energy_demand_kwh'].pct_change()*100)

    data_gen['perc_carbon_dif_vs_4G'] = round(data_gen.groupby(
                                    ['capacity', 'scenario', 'backhaul'])[
                                    'demand_carbon_per_kwh'].pct_change()*100)

    data_gen['perc_nitrogen_dif_vs_4G'] = round(data_gen.groupby(
                                    ['capacity', 'scenario', 'backhaul'])[
                                    'nitrogen_oxide_per_kwh'].pct_change()*100)

    data_gen['perc_sulpher_dif_vs_4G'] = round(data_gen.groupby(
                                    ['capacity', 'scenario', 'backhaul'])[
                                    'sulpher_dioxide_per_kwh'].pct_change()*100)

    data_gen['perc_pm10_dif_vs_4G'] = round(data_gen.groupby(
                                    ['capacity', 'scenario', 'backhaul'])[
                                    'pm10_per_kwh'].pct_change()*100)

    data_gen = data_gen.dropna()

    data = pd.merge(data,
            data_gen[['scenario', 'capacity', 'generation', 'backhaul',
            'perc_energy_dif_vs_4G',
            'perc_carbon_dif_vs_4G',
            'perc_nitrogen_dif_vs_4G',
            'perc_sulpher_dif_vs_4G',
            'perc_pm10_dif_vs_4G']],
            how='left',
            left_on=['scenario', 'capacity', 'generation', 'backhaul'],
            right_on = ['scenario', 'capacity', 'generation', 'backhaul']
        )

    # data_backhaul = data[['scenario', 'capacity', 'generation',
    #     'backhaul', 'total_annual_energy_demand_kwh',
    #     'demand_carbon_per_kwh', 'nitrogen_oxide_per_kwh',
    #     'sulpher_dioxide_per_kwh', 'pm10_per_kwh']].copy()

    # data_backhaul['w_over_fb'] = round(data_backhaul.groupby(
    #                                 ['scenario', 'capacity', 'generation'])[
    #                                 'social_cost'].pct_change()*100)
    # data_gen = data_gen.dropna()

    # data = pd.merge(data,
    #         data_backhaul[['scenario', 'capacity', 'generation', 'backhaul', 'w_over_fb']],
    #         how='left',
    #         left_on=['scenario', 'capacity', 'generation', 'backhaul'],
    #         right_on = ['scenario', 'capacity', 'generation', 'backhaul']
    #     )

    return data


if __name__ == '__main__':

    decision_options = [
        'technology_options',
        'business_model_options',
        'policy_options',
        'mixed_options',
        'energy_and_emissions',
    ]

    for decision_option in decision_options:
        for country in COUNTRY_LIST:

            iso3 = country['iso3']

            # if not iso3 == 'GMB':
            #     continue

            generate_percentages(iso3, decision_option)
