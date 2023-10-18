"""
Asset module
Author: Edward Oughton
Date: June 2021

"""
import math
from itertools import tee
import collections, functools, operator


def estimate_assets(country, region, option, costs, global_parameters,
    country_parameters):
    """
    Calculates the required number of assets.

    Parameters
    ----------
    region : dict
        The region being assessed and all associated parameters.
    option : str
        Infrastructure options covering the scenario and strategy.
    costs : dict
        Contains the costs of each necessary equipment item.
    global_parameters : dict
        Contains all global parameters.
    country_parameters :
        Contains all country parameters
    core_lut : dict
        Core assets by type and region.

    Returns
    -------
    assets : list of dicts
        Contains a list of assets by region.

    """
    strategy = option['strategy']

    total_existing_mno_sites = math.ceil(region['existing_mno_sites'])
    new_sites = math.ceil(region['new_mno_sites'])
    upgraded_sites = math.ceil(region['upgraded_mno_sites'])
    all_new_or_upgraded_sites = math.ceil(new_sites + upgraded_sites)
    existing_remaining_sites = math.ceil(total_existing_mno_sites - upgraded_sites)

    assets = []

    asset_structure = upgrade_sites(upgraded_sites, country, region)
    upgraded_assets = calc_assets(region, option, asset_structure,
                                costs, 'upgraded')
    assets = assets + upgraded_assets

    asset_structure = greenfield_sites(new_sites, country, region)
    new_assets = calc_assets(region, option, asset_structure,
                                costs, 'new')
    assets = assets + new_assets

    asset_structure = existing_sites(existing_remaining_sites, country, region)
    existing_assets = calc_assets(region, option, asset_structure,
                                costs, 'existing')
    assets = assets + existing_assets

    return assets


def upgrade_sites(upgraded_sites, country, region):
    """
    Asset structure for upgraded sites.

    """
    assets = {
        'equipment': upgraded_sites,
        'installation': upgraded_sites,
        'site_rental': upgraded_sites,
        'operation_and_maintenance': upgraded_sites,
        'backhaul': {
            'quantity': upgraded_sites,
            'backhaul_dist_m': get_backhaul_dist(country, region)
        },
    }

    return assets


def greenfield_sites(new_sites, country, region):
    """
    Asset structure for greenfield sites.

    """
    assets = {
        'equipment': new_sites,
        'site_build': new_sites,
        'installation': new_sites,
        'site_rental': new_sites,
        'operation_and_maintenance': new_sites,
        'backhaul': {
            'quantity': new_sites,
            'backhaul_dist_m': get_backhaul_dist(country, region)
        },
    }

    return assets


def existing_sites(existing_sites, country, region):
    """
    Asset structure for existing sites.

    """
    assets = {
        'site_rental': existing_sites,
        'operation_and_maintenance': existing_sites,
    }

    return assets


def get_backhaul_dist(country, region):
    """
    Calculate backhaul distance.
    # backhaul_fiber backhaul_copper backhaul_wireless	backhaul_satellite

    """
    nodes = math.ceil(
        math.ceil(region['existing_mno_sites']) *
        (country['backhaul_fiber_perc']/100)
    )
    node_density_km2 = nodes / region['area_km2']

    if node_density_km2 > 0:
        ave_distance_to_a_node_m = (math.sqrt(1/node_density_km2) / 2) * 1000
    else:
        ave_distance_to_a_node_m = round(math.sqrt(region['area_km2']) * 1000) / 2

    return ave_distance_to_a_node_m


def calc_assets(region, option, asset_structure, costs, build_type):
    """
    Calculate the number of assets.

    """
    backhaul = option['strategy'].split('_')[2]
    geotype = region['geotype'].split(' ')[0]
    new_backhaul = region['backhaul_new']

    total_assets = []

    for asset_name1, quantity in asset_structure.items():

        if asset_name1 == 'site_rental':
            asset_name1 = asset_name1 + '_' + geotype

        backhaul_units = 0
        if asset_name1 == 'backhaul' and new_backhaul == 0:
            quantity = 0
            cost_per_unit = 0
        elif asset_name1 == 'backhaul' and new_backhaul > 0:
            backhaul_dist_m = math.ceil(quantity['backhaul_dist_m'])
            quantity = quantity['quantity']
            backhaul_units, backhaul_name = estimate_backhaul_type(
                backhaul,
                backhaul_dist_m,
                geotype)
            cost_per_unit = costs[backhaul_name]
            asset_name1 = asset_name1 + '_' + backhaul_name

            if  backhaul == 'fiber':
                #cost = cost_per_meter * number_of_sites * backaul_length_m
                total_cost = cost_per_unit * quantity * backhaul_units
            if backhaul == 'wireless':
                #cost = cost_per_backhaul_unit * number_of_sites * number_of_backhaul_units (e.g., 2 per site)
                total_cost = cost_per_unit * quantity * backhaul_units

        else:
            cost_per_unit = costs[asset_name1]
            total_cost = cost_per_unit * quantity

        total_assets.append({
            'scenario': region['scenario'],
            'strategy': option['strategy'],
            'confidence': region['confidence'],
            'decile': region['decile'],
            'asset': asset_name1,
            'quantity': quantity,
            'cost_per_unit': cost_per_unit,
            'backhaul_units': backhaul_units,
            'total_cost': total_cost,
            'build_type': build_type,
            'ownership': 'mno',
        })

    return total_assets


def estimate_backhaul_type(backhaul, ave_distance_to_a_node_m, geotype):
    """
    Estimate the type of backhaul and associated costs.

    """
    if backhaul == 'wireless':
        if ave_distance_to_a_node_m < 15000:
            quantity = 1
            return quantity, '{}_{}'.format(backhaul, 'small')
        elif 15000 < ave_distance_to_a_node_m < 30000:
            quantity = 1
            return quantity, '{}_{}'.format(backhaul, 'medium')
        elif 30000 < ave_distance_to_a_node_m < 45000:
            quantity = 1
            return quantity, '{}_{}'.format(backhaul, 'large')
        else:
            quantity = int(math.ceil(ave_distance_to_a_node_m / 45000))
            return quantity, '{}_{}'.format(backhaul, 'large')

    elif backhaul == 'fiber':
        quantity = ave_distance_to_a_node_m
        return quantity, '{}_{}_m'.format(backhaul, geotype)

    else:
        print('Did not recognise the backhaul technology {}'.format(backhaul))
        return 0, 'Backhaul tech not recognized'
