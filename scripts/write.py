"""
Functions for writing to .csv

September 2020

Written by Ed Oughton

"""
import os
import pandas as pd
import datetime


# def define_deciles(regions):
#     """
#     Allocate deciles to regions.

#     """
#     regions = regions.sort_values(by='population_km2', ascending=True)

#     regions['decile'] = regions.groupby([
#         'GID_0',
#         'scenario',
#         'strategy',
#         'confidence'
#     ], as_index=True).population_km2.apply( #cost_per_sp_user
#         pd.qcut, q=11, precision=0,
#         labels=[100,90,80,70,60,50,40,30,20,10,0],
#         duplicates='drop') #   [0,10,20,30,40,50,60,70,80,90,100]

#     return regions


def write_demand(regional_annual_demand, folder):
    """
    Write all annual demand results.

    """
    # print('Writing annual_mno_demand')
    regional_annual_demand = pd.DataFrame(regional_annual_demand)
    regional_annual_demand = regional_annual_demand.drop_duplicates()
    regional_annual_market_demand = regional_annual_demand[[
        'GID_0', 'decile', 'scenario', 'strategy',
        'confidence', 'year', 'population',
        # 'population_f_over_10', 'population_m_over_10',
        'area_km2', 'population_km2',
        'geotype', 'arpu_discounted_monthly',
        # 'penetration_female',
        # 'penetration_male',
        'penetration',
        'population_with_phones',
        # 'population_with_phones_f_over_10',
        # 'population_with_phones_m_over_10',
        'smartphone_penetration',
        'population_with_smartphones',
        # 'population_with_smartphones_f_over_10',
        # 'population_with_smartphones_m_over_10',
        'revenue'
    ]]
    filename = 'regional_annual_market_demand.csv'
    path = os.path.join(folder, filename)
    regional_annual_market_demand.to_csv(path, index=True)


def write_results(regional_results, folder, metric):
    """
    Write all results.

    """
    # print('Writing national MNO results')
    national_results = pd.DataFrame(regional_results)
    national_results = national_results[[
        'GID_0', 'scenario', 'strategy', 'confidence', 'population_total', 'area_km2',
        'phones_on_network', 'smartphones_on_network', 'total_estimated_sites',
        'existing_mno_sites', 'upgraded_mno_sites', 'new_mno_sites',
        'total_mno_revenue', 'total_mno_cost',
    ]]
    national_results = national_results.drop_duplicates()
    national_results = national_results.groupby([
        'GID_0', 'scenario', 'strategy', 'confidence'], as_index=True).sum()
    national_results['cost_per_network_user'] = (
        national_results['total_mno_cost'] / national_results['phones_on_network'])
    national_results['cost_per_smartphone_user'] = (
        national_results['total_mno_cost'] / national_results['smartphones_on_network'])
    path = os.path.join(folder,'national_mno_results_{}.csv'.format(metric))
    national_results.to_csv(path, index=True)


    # print('Writing national cost composition results')
    national_cost_results = pd.DataFrame(regional_results)
    national_cost_results = national_cost_results[[
        'GID_0', 'scenario', 'strategy', 'confidence', 'population_total',
        'phones_on_network', 'smartphones_on_network', 'total_mno_revenue',
        'ran', 'backhaul_fronthaul', 'civils', 'core_network',
        'administration', 'spectrum_cost', 'tax', 'profit_margin',
        'total_mno_cost', 'available_cross_subsidy', 'deficit',
        'used_cross_subsidy', 'required_state_subsidy',
    ]]
    national_cost_results = national_cost_results.drop_duplicates()
    national_cost_results = national_cost_results.groupby([
        'GID_0', 'scenario', 'strategy', 'confidence'], as_index=True).sum()
    national_cost_results['cost_per_network_user'] = (
        national_cost_results['total_mno_cost'] /
        national_cost_results['phones_on_network'])
    national_cost_results['cost_per_smartphone_user'] = (
        national_cost_results['total_mno_cost'] /
        national_cost_results['smartphones_on_network'])
    #Calculate private, govt and societal costs
    national_cost_results['private_cost'] = national_cost_results['total_mno_cost']
    national_cost_results['government_cost'] = (
        national_cost_results['required_state_subsidy'] -
            (national_cost_results['spectrum_cost'] + national_cost_results['tax']))
    national_cost_results['societal_cost'] = (
        national_cost_results['private_cost'] + national_cost_results['government_cost'])
    path = os.path.join(folder,'national_mno_cost_results_{}.csv'.format(metric))
    national_cost_results.to_csv(path, index=True)


    # print('Writing general decile results')
    decile_results = pd.DataFrame(regional_results)
    # decile_results = define_deciles(decile_results)
    decile_results = decile_results[[
        'GID_0', 'scenario', 'strategy', 'decile', 'confidence',
        'population_total', 'area_km2', 'phones_on_network',
        'smartphones_on_network', 'total_estimated_sites',
        'existing_mno_sites', 'upgraded_mno_sites', 'new_mno_sites',
        'total_mno_revenue', 'total_mno_cost',
    ]]
    decile_results = decile_results.drop_duplicates()
    decile_results = decile_results.groupby([
        'GID_0', 'scenario', 'strategy', 'confidence', 'decile'], as_index=True).sum()
    decile_results['population_km2'] = (
        decile_results['population_total'] / decile_results['area_km2'])
    decile_results['phone_density_on_network_km2'] = (
        decile_results['phones_on_network'] / decile_results['area_km2'])
    decile_results['sp_density_on_network_km2'] = (
        decile_results['smartphones_on_network'] / decile_results['area_km2'])
    decile_results['total_estimated_sites_km2'] = (
        decile_results['total_estimated_sites'] / decile_results['area_km2'])
    decile_results['existing_mno_sites_km2'] = (
        decile_results['existing_mno_sites'] / decile_results['area_km2'])
    decile_results['cost_per_network_user'] = (
        decile_results['total_mno_cost'] / decile_results['phones_on_network'])
    decile_results['cost_per_smartphone_user'] = (
        decile_results['total_mno_cost'] / decile_results['smartphones_on_network'])
    path = os.path.join(folder,'decile_mno_results_{}.csv'.format(metric))
    decile_results.to_csv(path, index=True)


    # print('Writing cost decile results')
    decile_cost_results = pd.DataFrame(regional_results)
    # decile_cost_results = define_deciles(decile_cost_results)
    decile_cost_results = decile_cost_results[[
        'GID_0', 'scenario', 'strategy', 'decile', 'confidence',
        'population_total', 'area_km2', 'phones_on_network', 'smartphones_on_network',
        'total_mno_revenue', 'ran', 'backhaul_fronthaul', 'civils', 'core_network',
        'administration', 'spectrum_cost', 'tax', 'profit_margin', 'total_mno_cost',
        'available_cross_subsidy', 'deficit', 'used_cross_subsidy',
        'required_state_subsidy',
    ]]
    decile_cost_results = decile_cost_results.drop_duplicates()
    decile_cost_results = decile_cost_results.groupby([
        'GID_0', 'scenario', 'strategy', 'confidence', 'decile'], as_index=True).sum()
    decile_cost_results['cost_per_network_user'] = (
        decile_cost_results['total_mno_cost'] / decile_cost_results['phones_on_network'])
    decile_cost_results['cost_per_smartphone_user'] = (
        decile_cost_results['total_mno_cost'] / decile_cost_results['smartphones_on_network'])
    path = os.path.join(folder,'decile_mno_cost_results_{}.csv'.format(metric))
    decile_cost_results.to_csv(path, index=True)


    # # print('Writing regional results')
    # regional_mno_results = pd.DataFrame(regional_results)
    # # regional_mno_results = define_deciles(regional_mno_results)
    # regional_mno_results = regional_mno_results[[
    #     'GID_0', 'decile', 'scenario', 'strategy', 'decile',
    #     'confidence', 'population_total', 'area_km2',
    #     'phones_on_network', 'smartphones_on_network',
    #     'total_estimated_sites', 'existing_mno_sites',
    #     'upgraded_mno_sites', 'new_mno_sites',
    #     'total_mno_revenue', 'total_mno_cost',
    # ]]
    # regional_mno_results = regional_mno_results.drop_duplicates()
    # regional_mno_results['cost_per_network_user'] = (
    #     regional_mno_results['total_mno_cost'] / regional_mno_results['phones_on_network'])
    # regional_mno_results['cost_per_smartphone_user'] = (
    #     regional_mno_results['total_mno_cost'] / regional_mno_results['smartphones_on_network'])
    # path = os.path.join(folder,'regional_mno_results_{}.csv'.format(metric))
    # regional_mno_results.to_csv(path, index=True)


    # print('Writing national market results')
    national_results = pd.DataFrame(regional_results)
    national_results = national_results[[
        'GID_0', 'scenario', 'strategy', 'confidence',
        'population_total', 'area_km2',
        'total_phones', 'total_smartphones',
        'total_estimated_sites',
        'total_upgraded_sites',
        'total_new_sites',
        'total_market_revenue', 'total_market_cost',
        'total_spectrum_cost', 'total_tax',
        'total_required_state_subsidy',
    ]]
    national_results = national_results.drop_duplicates()
    national_results = national_results.groupby([
        'GID_0', 'scenario', 'strategy', 'confidence'], as_index=True).sum()
    national_results['cost_per_network_user'] = (
        national_results['total_market_cost'] / national_results['total_phones'])
    national_results['cost_per_smartphone_user'] = (
        national_results['total_market_cost'] / national_results['total_smartphones'])
    national_results['private_cost'] = (
        national_results['total_market_cost'])
    national_results['government_cost'] = (
        national_results['total_required_state_subsidy'] -
            (national_results['total_spectrum_cost'] + national_results['total_tax']))
    national_results['social_cost'] = (
        national_results['private_cost'] + national_results['government_cost'])
    path = os.path.join(folder,'national_market_results_{}.csv'.format(metric))
    # national_results.reset_index(drop=False, inplace=True)
    national_results.to_csv(path, index=True)


    #=cost / market share * 100
    # print('Writing national market cost composition results')
    national_cost_results = pd.DataFrame(regional_results)
    national_cost_results = national_cost_results[[
        'GID_0', 'scenario', 'strategy', 'confidence', 'population_total',
        'total_phones', 'total_smartphones',
        'total_market_revenue', 'total_ran', 'total_backhaul_fronthaul',
        'total_civils', 'total_core_network',
        'total_administration', 'total_spectrum_cost',
        'total_tax', 'total_profit_margin',
        'total_market_cost', 'total_available_cross_subsidy',
        'total_deficit', 'total_used_cross_subsidy',
        'total_required_state_subsidy',
    ]]
    national_cost_results = national_cost_results.drop_duplicates()
    national_cost_results = national_cost_results.groupby([
        'GID_0', 'scenario', 'strategy', 'confidence'], as_index=True).sum()
    national_cost_results['cost_per_network_user'] = (
        national_cost_results['total_market_cost'] / national_cost_results['total_phones'])
    national_cost_results['cost_per_smartphone_user'] = (
        national_cost_results['total_market_cost'] / national_cost_results['total_smartphones'])
    #Calculate private, govt and societal costs
    national_cost_results['private_cost'] = (
        national_cost_results['total_market_cost'])
    national_cost_results['government_cost'] = (
        national_cost_results['total_required_state_subsidy'] -
            (national_cost_results['total_spectrum_cost'] + national_cost_results['total_tax']))
    national_cost_results['societal_cost'] = (
        national_cost_results['private_cost'] + national_cost_results['government_cost'])
    path = os.path.join(folder,'national_market_cost_results_{}.csv'.format(metric))
    national_cost_results.to_csv(path, index=True)

    # print('Writing general decile results')
    decile_results = pd.DataFrame(regional_results)
    # decile_results = define_deciles(decile_results)
    decile_results = decile_results[[
        'GID_0', 'scenario', 'strategy', 'decile', 'confidence',
        'population_total', 'area_km2', 'total_phones', 'total_smartphones',
        'total_market_revenue', 'total_market_cost',
    ]]
    decile_results = decile_results.drop_duplicates()
    decile_results = decile_results.groupby([
        'GID_0', 'scenario', 'strategy', 'confidence', 'decile'], as_index=True).sum()
    decile_results['population_km2'] = (
        decile_results['population_total'] / decile_results['area_km2'])
    decile_results['cost_per_network_user'] = (
        decile_results['total_market_cost'] / decile_results['total_phones'])
    decile_results['cost_per_smartphone_user'] = (
        decile_results['total_market_cost'] / decile_results['total_smartphones'])
    path = os.path.join(folder,'decile_market_results_{}.csv'.format(metric))
    decile_results.to_csv(path, index=True)


    # print('Writing cost decile results')
    decile_cost_results = pd.DataFrame(regional_results)
    # decile_cost_results = define_deciles(decile_cost_results)
    decile_cost_results = decile_cost_results[[
        'GID_0', 'scenario', 'strategy', 'decile', 'confidence',
        'population_total', 'area_km2', 'population_km2', 'total_phones',
        'total_smartphones', 'total_market_revenue', 'total_ran',
        'total_backhaul_fronthaul', 'total_civils', 'total_core_network',
        'total_administration', 'total_spectrum_cost', 'total_tax',
        'total_profit_margin', 'total_market_cost',
        'total_available_cross_subsidy', 'total_deficit',
        'total_used_cross_subsidy', 'total_required_state_subsidy'
    ]]
    decile_cost_results = decile_cost_results.drop_duplicates()
    decile_cost_results = decile_cost_results.groupby([
        'GID_0', 'scenario', 'strategy', 'confidence', 'decile'], as_index=True).sum()
    decile_cost_results['cost_per_network_user'] = (
        decile_cost_results['total_market_cost'] /
        decile_cost_results['total_phones'])
    decile_cost_results['cost_per_smartphone_user'] = (
        decile_cost_results['total_market_cost'] /
        decile_cost_results['total_smartphones'])
    decile_cost_results['private_cost'] = (
        decile_cost_results['total_market_cost'])
    decile_cost_results['government_cost'] = (
        decile_cost_results['total_required_state_subsidy'] -
            (decile_cost_results['total_spectrum_cost'] + decile_cost_results['total_tax']))
    decile_cost_results['societal_cost'] = (
        decile_cost_results['private_cost'] + decile_cost_results['government_cost'])
    path = os.path.join(folder,'decile_market_cost_results_{}.csv'.format(metric))
    decile_cost_results.to_csv(path, index=True)


    # print('Writing regional results')
    regional_market_results = pd.DataFrame(regional_results)
    # regional_market_results = define_deciles(regional_market_results)
    # regional_market_results = regional_market_results[[
    #     'GID_0', 'decile', 'scenario', 'strategy', 'decile', 'geotype',
    #     'confidence', 'population_total', 'area_km2',
    #     'total_phones', 'total_smartphones',
    #     'total_upgraded_sites','total_new_sites',
    #     'total_required_state_subsidy', 'total_spectrum_cost',
    #     'total_tax', 'total_market_revenue', 'total_market_cost',
    # ]]
    regional_market_results = regional_market_results.drop_duplicates()

    regional_market_results['total_private_cost'] = regional_market_results['total_market_cost']
    regional_market_results['total_government_cost'] = (
        regional_market_results['total_required_state_subsidy'] -
            (regional_market_results['total_spectrum_cost'] +
            regional_market_results['total_tax']))
    regional_market_results['total_societal_cost'] = (
        regional_market_results['total_private_cost'] +
        regional_market_results['total_government_cost'])

    regional_market_results['private_cost_per_network_user'] = (
        regional_market_results['total_private_cost'] /
        regional_market_results['total_phones'])
    regional_market_results['government_cost_per_network_user'] = (
        regional_market_results['total_government_cost'] /
        regional_market_results['total_phones'])
    regional_market_results['societal_cost_per_network_user'] = (
        regional_market_results['total_societal_cost'] /
        regional_market_results['total_phones'])

    regional_market_results['private_cost_per_smartphone_user'] = (
        regional_market_results['total_private_cost'] /
        regional_market_results['total_smartphones'])
    regional_market_results['government_cost_per_smartphone_user'] = (
        regional_market_results['total_government_cost'] /
        regional_market_results['total_smartphones'])
    regional_market_results['societal_cost_per_network_user'] = (
        regional_market_results['total_societal_cost'] /
        regional_market_results['total_smartphones'])

    path = os.path.join(folder,'regional_market_results_{}.csv'.format(metric))
    regional_market_results.to_csv(path, index=True)


def write_inputs(folder, country, country_parameters, global_parameters,
    costs, decision_option):
    """
    Write model inputs.

    """
    country_info = pd.DataFrame(country.items(),
        columns=['parameter', 'value'])
    country_info['source'] = 'country_info'

    country_params = pd.DataFrame(
        country_parameters['financials'].items(),
        columns=['parameter', 'value'])
    country_params['source'] = 'country_parameters'

    global_parameters = pd.DataFrame(global_parameters.items(),
        columns=['parameter', 'value'])
    global_parameters['source'] = 'global_parameters'

    costs = pd.DataFrame(costs.items(),
        columns=['parameter', 'value'])
    costs['source'] = 'costs'

    parameters = pd.concat([country_info, country_params, global_parameters, costs])
    parameters = parameters[['source', 'parameter', 'value']]

    timenow = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

    filename = 'parameters_{}_{}.csv'.format(decision_option, timenow)
    path = os.path.join(folder, filename)
    parameters.to_csv(path, index=True)


def write_energy(data_energy, folder, metric):
    """
    Write all energy consumption.

    """
    # print('Writing energy')
    # print('write_energy: {}'.format(len(data_energy)))
    data_energy = pd.DataFrame(data_energy)

    path = os.path.join(folder,'energy_{}.csv'.format(metric))
    data_energy.to_csv(path, index=True)


def write_energy_aggregated(data_energy, regional_annual_demand, folder, metric):
    """
    Write energy.

    """
    # print('Writing energy aggregated')
    # print('write_energy_aggregated: {}'.format(len(data_energy)))
    df = pd.DataFrame(data_energy)
    df = df.drop_duplicates()
    df = df[[
        'GID_0', 'income', 'scenario', 'strategy',
        'confidence', 'grid_type', 'asset_type','asset_type',
        'mno_energy_annual_demand_kwh',
        'mno_equipment_annual_demand_kWh',
        'mno_regional_nodes_annual_demand_kwh',
        'mno_core_nodes_annual_demand_kwh',
        'mno_wireless_backhaul_annual_demand_kwh',
        'total_energy_annual_demand_kwh',
        'total_equipment_annual_demand_kWh',
        'total_regional_nodes_annual_demand_kwh',
        'total_core_nodes_annual_demand_kwh',
        'total_wireless_backhaul_annual_demand_kwh',

    ]]
    df = df.groupby([
        'GID_0', 'scenario', 'strategy', 'confidence'], as_index=True).sum()
    path = os.path.join(folder,'energy_national_{}.csv'.format(metric))
    df.to_csv(path, index=True)


def write_energy_annual_aggregated(data_energy, regional_annual_demand, folder, metric):
    """
    Write energy.

    """
    # print('Writing energy aggregated')
    # print('write_energy_annual_aggregated: {}'.format(len(data_energy)))
    df = pd.DataFrame(data_energy)
    df = df.drop_duplicates()
    df = df[[
        'GID_0', 'income', 'year', 'scenario', 'strategy', 'confidence', 'asset_type', 'grid_type',

        'mno_energy_annual_demand_kwh',
        'mno_equipment_annual_demand_kWh',
        'mno_regional_nodes_annual_demand_kwh',
        'mno_core_nodes_annual_demand_kwh',
        'mno_wireless_backhaul_annual_demand_kwh',
        'total_energy_annual_demand_kwh',
        'total_equipment_annual_demand_kWh',
        'total_regional_nodes_annual_demand_kwh',
        'total_core_nodes_annual_demand_kwh',
        'total_wireless_backhaul_annual_demand_kwh',

    ]]
    df = df.groupby([
        'GID_0', 'income', 'year', 'scenario', 'strategy', 'confidence'], as_index=True).sum()

    regional_annual_demand = pd.DataFrame(regional_annual_demand)
    regional_annual_demand = regional_annual_demand.drop_duplicates()
    regional_annual_demand = regional_annual_demand[[
        'GID_0', 'income', 'scenario', 'strategy',
        'confidence', 'year', 'population',
        'area_km2', 'population_with_phones',
        'population_with_smartphones',
    ]]
    regional_annual_demand = regional_annual_demand.groupby([
        'GID_0', 'income', 'year', 'scenario', 'strategy', 'confidence'], as_index=True).sum()
    df = df.merge(regional_annual_demand,
        left_on=['GID_0', 'income', 'year', 'scenario', 'strategy', 'confidence'],
        right_on=['GID_0', 'income', 'year', 'scenario', 'strategy', 'confidence'])

    path = os.path.join(folder,'energy_national_annual_{}.csv'.format(metric))
    df.to_csv(path, index=True)


def write_assets(all_assets, folder, metric):
    """
    Write all planned assets.

    """
    # print('Writing assets')
    all_assets = pd.DataFrame(all_assets)

    path = os.path.join(folder,'assets_{}.csv'.format(metric))
    all_assets.to_csv(path, index=True)


def write_emissions(emissions, folder, metric):
    """
    Write all emissions.

    """
    # print('Writing emissions')
    emissions = pd.DataFrame(emissions)

    path = os.path.join(folder,'emissions_{}.csv'.format(metric))
    emissions.to_csv(path, index=True)


def write_emissions_aggregated(emissions, folder, metric):
    """
    Write all emissions.

    """
    # print('Writing emissions aggregated')

    df = pd.DataFrame(emissions)
    df = df.drop_duplicates()
    df = df[[
        'GID_0', 'income', 'scenario', 'strategy', 'asset_type', 'confidence',
        # 'population','population_with_phones', 'population_with_smartphones',
        'mno_energy_annual_demand_kwh',
        'mno_demand_carbon_tonnes',
        'mno_nitrogen_oxide_tonnes',
        'mno_sulpher_dioxide_tonnes',
        'mno_pm10_tonnes',
        'total_energy_annual_demand_kwh',
        'total_demand_carbon_tonnes',
        'total_nitrogen_oxide_tonnes',
        'total_sulpher_dioxide_tonnes',
        'total_pm10_tonnes'
    ]]
    df = df.groupby([
        'GID_0', 'income', 'scenario', 'strategy', 'asset_type','confidence'], as_index=True).sum()
    path = os.path.join(folder,'emissions_national_{}.csv'.format(metric))
    df.to_csv(path, index=True)


def write_emissions_annual_aggregated(emissions, regional_annual_demand, folder, metric):
    """
    Write all emissions.

    """
    # print('Writing emissions aggregated')

    df = pd.DataFrame(emissions)
    df = df.drop_duplicates()
    df = df[[
        'year', 'GID_0', 'income', 'scenario', 'strategy', 'confidence', #'asset_type',
        # 'total_sites',
        # 'total_upgraded_sites',
        # 'total_new_sites',
        'mno_energy_annual_demand_kwh',
        'mno_demand_carbon_tonnes',
        'mno_nitrogen_oxide_tonnes',
        'mno_sulpher_dioxide_tonnes',
        'mno_pm10_tonnes',
        'total_energy_annual_demand_kwh',
        'total_demand_carbon_tonnes',
        'total_nitrogen_oxide_tonnes',
        'total_sulpher_dioxide_tonnes',
        'total_pm10_tonnes'
    ]]
    df = df.groupby([
        'income', 'year', 'GID_0', 'scenario', 'strategy'], as_index=True).sum() #, 'asset_type'

    regional_annual_demand = pd.DataFrame(regional_annual_demand)
    regional_annual_demand = regional_annual_demand.drop_duplicates()
    regional_annual_demand = regional_annual_demand[[
        'GID_0', 'income', 'scenario', 'strategy',
        'confidence', 'year', 'population',
        'area_km2', 'population_with_phones',
        'population_with_smartphones',
    ]]
    regional_annual_demand = regional_annual_demand.groupby([
        'GID_0', 'income', 'year', 'scenario', 'strategy', 'confidence'], as_index=True).sum()
    df = df.merge(regional_annual_demand,
        left_on=['GID_0', 'income', 'year', 'scenario', 'strategy', 'confidence'],
        right_on=['GID_0', 'income', 'year', 'scenario', 'strategy', 'confidence'])

    path = os.path.join(folder,'emissions_national_annual_{}.csv'.format(metric))
    df.to_csv(path, index=True)


def write_power_emissions(emissions, folder, metric):
    """
    Write all emissions.

    """
    # print('Writing emissions aggregated')
    df = pd.DataFrame(emissions)
    df = df.drop_duplicates()
    df = df[[
        'GID_0', 'income', 'scenario', 'strategy', 'confidence', 'asset_type', 'grid_type',
        # 'population','population_with_phones', 'population_with_smartphones',
        'mno_energy_annual_demand_kwh',
        'mno_demand_carbon_tonnes',
        'mno_nitrogen_oxide_tonnes',
        'mno_sulpher_dioxide_tonnes',
        'mno_pm10_tonnes',
        'total_energy_annual_demand_kwh',
        'total_demand_carbon_tonnes',
        'total_nitrogen_oxide_tonnes',
        'total_sulpher_dioxide_tonnes',
        'total_pm10_tonnes'
    ]]
    df = df.groupby([
        'GID_0', 'income', 'scenario', 'strategy', 'confidence', 'asset_type', 'grid_type'], as_index=True).sum()
    path = os.path.join(folder,'power_emissions_{}.csv'.format(metric))
    df.to_csv(path, index=True)
