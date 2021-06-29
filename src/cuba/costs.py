"""
Cost module
Author: Edward Oughton
Date: June 2021

"""
import math
from itertools import tee
import collections, functools, operator


def find_cost(region, assets, option, costs, global_parameters,
    country_parameters, infra_sharing_assets, cost_types):
    """
    Calculates the annual total cost using capex and opex.

    Parameters
    ----------
    region : dict
        The region being assessed and all associated parameters.
    assets : list of dicts
        Contains all assets.
    option : str
        Infrastructure options covering the scenario and strategy.
    costs : dict
        Contains the costs of each necessary equipment item.
    global_parameters : dict
        Contains all global parameters.
    country_parameters : dict
        Contains all country parameters.
    infra_sharing_assets : dict
        Shared infra assets lookup by strategy (e.g. passive,
        active or srn).
    cost_types : dict
        Cost types lookup (e.g. capex, opex or both).

    Returns
    -------
    output : list of dicts
        Contains a list of costs, with affliated discounted capex and
        opex costs.

    """
    regional_asset_cost = calc_sharing(assets, region, option,
        country_parameters, infra_sharing_assets)

    regional_asset_cost = calc_npv(regional_asset_cost, cost_types, global_parameters,
        country_parameters)

    aggregated_cost = aggregate_costs(regional_asset_cost)

    network_cost = 0
    for k, v in aggregated_cost.items():
        region[k] = v
        network_cost += v

    region['network_cost'] = network_cost

    return region


def calc_sharing(assets, region, option, country_parameters, infra_sharing_assets):
    """
    Reflects the baseline scenario of needing to build a single dedicated
    network.

    """
    sharing = option['strategy'].split('_')[3]
    geotype = region['geotype'].split(' ')[0]
    networks = country_parameters['networks']['baseline' + '_' + geotype]

    shared_assets = infra_sharing_assets[sharing]

    all_keys = set()

    for item in assets:
        all_keys.add(item['asset'])

    cost_structure = {}

    for key in list(all_keys):
        value = 0
        for item in assets:
            if key == item['asset']:
                value += item['total_cost']

        if not key in shared_assets:
            cost_structure[key] = value
        else:
            if sharing == 'srn':
                if geotype == 'urban' or geotype == 'suburban':
                    cost_structure[key] = value
                else:
                    cost_structure[key] = value / networks
            else:
                cost_structure[key] = value / networks

    return cost_structure


def calc_npv(assets, cost_types, global_parameters, country_parameters):
    """
    Add the time dimension and get the Net Present Value (NPV).

    """
    cost_by_asset = []

    total_cost = 0

    for asset_name1, cost in assets.items():
        for asset_name2, type_of_cost in cost_types.items():
            if asset_name1 == asset_name2:

                if type_of_cost == 'capex_and_opex':

                    cost = discount_capex_and_opex(cost, global_parameters,
                        country_parameters)

                elif type_of_cost == 'capex':

                    cost = cost * (1 + (country_parameters['financials']['wacc'] / 100))

                elif type_of_cost == 'opex':

                    cost = discount_opex(cost, global_parameters, country_parameters)

                else:
                    return 'Did not recognize cost type'

                total_cost += cost

                cost_by_asset.append({
                    'asset': asset_name1,
                    'cost': cost,
                })

    cost_by_asset = {item['asset']: item['cost'] for item in cost_by_asset}

    return cost_by_asset


def aggregate_costs(cost_by_asset):
    """
    Aggregate the costs.

    """
    ran = [
        'equipment',
        'site_rental',
        'operation_and_maintenance',
        'power',
    ]

    backhaul_fronthaul = [
        'backhaul',
    ]

    civils = [
        'site_build',
        'installation',
    ]

    core = [
        'regional_node',
        'regional_edge',
        'core_node',
        'core_edge',
    ]

    ran_cost = 0
    backhaul_fronthaul_cost = 0
    civils_cost = 0
    core_cost = 0

    for key, value in cost_by_asset.items():
        if key in ran:
            ran_cost += value
        if key in backhaul_fronthaul:
            backhaul_fronthaul_cost += value
        if key in civils:
             civils_cost += value
        if key in core:
            core_cost += value

    aggregated_cost = {
        'ran': ran_cost,
        'backhaul_fronthaul': backhaul_fronthaul_cost,
        'civils': civils_cost,
        'core_network': core_cost,
    }

    return aggregated_cost


def discount_capex_and_opex(capex, global_parameters, country_parameters):
    """
    Discount costs based on return period.

    Parameters
    ----------
    cost : float
        Financial cost.
    global_parameters : dict
        All global model parameters.

    Returns
    -------
    discounted_cost : float
        The discounted cost over the desired time period.

    """
    return_period = global_parameters['return_period']
    discount_rate = global_parameters['discount_rate'] / 100
    wacc = country_parameters['financials']['wacc']

    costs_over_time_period = []

    costs_over_time_period.append(capex)

    opex = round(float(capex) *
        (float(global_parameters['opex_percentage_of_capex']) / 100))

    for i in range(0, return_period):
        costs_over_time_period.append(
            opex / (1 + discount_rate)**i
        )

    discounted_cost = round(sum(costs_over_time_period))

    #add wacc
    discounted_cost = discounted_cost * (1 + (wacc/100))

    return discounted_cost


def discount_opex(opex, global_parameters, country_parameters):
    """
    Discount opex based on return period.

    """
    return_period = global_parameters['return_period']
    discount_rate = global_parameters['discount_rate'] / 100
    wacc = country_parameters['financials']['wacc']

    costs_over_time_period = []

    for i in range(0, return_period):
        costs_over_time_period.append(
            opex / (1 + discount_rate)**i
        )

    discounted_cost = round(sum(costs_over_time_period))

    #add wacc
    discounted_cost = discounted_cost * (1 + (wacc/100))

    return discounted_cost
