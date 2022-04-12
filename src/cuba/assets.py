"""
Asset module
Author: Edward Oughton
Date: June 2021

"""
import math
from itertools import tee
import collections, functools, operator


def estimate_assets(region, option, costs, global_parameters,
    country_parameters, core_lut):
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

    new_sites = region['new_mno_sites']
    upgraded_sites = region['upgraded_mno_sites']
    all_sites = new_sites + upgraded_sites

    new_backhaul = region['backhaul_new']

    assets = []

    for i in range(1, int(all_sites) + 1):

        if i <= upgraded_sites:

            asset_structure = upgrade_site(region, strategy, costs, core_lut)

            total_assets = calc_assets(region, option, asset_structure, i,
                                        new_backhaul, costs, 'upgraded')

            assets = assets + total_assets

        if i > upgraded_sites:

            asset_structure = greenfield_site(region, strategy, costs, core_lut)

            total_assets = calc_assets(region, option, asset_structure, i,
                                        new_backhaul, costs, 'new')

            assets = assets + total_assets

    core_assets = estimate_core_assets(region, option, costs, core_lut)
    assets = assets + core_assets

    return assets


def upgrade_site(region, strategy, costs, core_lut):
    """
    Reflects the baseline scenario of needing to build a single dedicated
    network.

    """

    assets = {
        'equipment': 1,
        'installation': 1,
        'site_rental': 1,
        'operation_and_maintenance': 1,
        # 'power': costs['power'],
        'backhaul': get_backhaul_dist(region, core_lut),
    }

    return assets


def greenfield_site(region, strategy, costs, core_lut):
    """
    Build a greenfield asset.

    """
    # backhaul = '{}_backhaul'.format(strategy.split('_')[2])
    # geotype = region['geotype'].split(' ')[0]

    assets = {
        'equipment': 1,
        'site_build': 1,
        'installation': 1,
        'site_rental': 1,
        'operation_and_maintenance': 1,
        # 'power': costs['power'],
        'backhaul': get_backhaul_dist(region, core_lut),
    }

    return assets


def estimate_core_assets(region, option, costs, core_lut):
    """
    Reflects the baseline scenario of needing to build a single dedicated
    network.

    """
    backhaul_type = option['strategy'].split('_')[2]

    core_assets = []

    build_types = [
        'new',
        'existing',
    ]

    asset_types = [
        'core_edge',
        'core_node',
        'regional_edge',
        'regional_node',
    ]

    for build_type in build_types:
        for asset_type in asset_types:

            if asset_type == 'regional_node' and backhaul_type == 'wireless':
                continue

            if asset_type == 'regional_edge' and backhaul_type == 'wireless':
                continue

            cost_per_unit = costs[asset_type]

            if asset_type.startswith('core'):
                quantity = core_net_assets(region, asset_type, build_type, core_lut)
            if asset_type.startswith('regional'):
                quantity = regional_net_assets(region, asset_type, build_type, core_lut)

            core_assets.append({
                    'scenario': region['scenario'],
                    'strategy': region['strategy'],
                    'confidence': region['confidence'],
                    'GID_id': region['GID_id'],
                    'asset': asset_type,
                    'quantity': quantity,
                    'cost_per_unit': cost_per_unit,
                    'total_cost': quantity * cost_per_unit,
                    'build_type': build_type,
            })

    return core_assets


def get_backhaul_dist(region, core_lut):
    """
    Calculate backhaul distance.
    # backhaul_fiber backhaul_copper backhaul_wireless	backhaul_satellite

    """
    nodes = 0
    for asset_type in ['core_node', 'regional_node']:
        for status in ['new', 'existing']:
            combined_key = '{}_{}'.format(region['GID_id'], status)
            if 'core_node' in core_lut:
                nodes += core_lut[asset_type][combined_key]

    node_density_km2 = nodes / region['area_km2']

    if node_density_km2 > 0:
        ave_distance_to_a_node_m = (math.sqrt(1/node_density_km2) / 2) * 1000
    else:
        ave_distance_to_a_node_m = round(math.sqrt(region['area_km2']) * 1000)

    return ave_distance_to_a_node_m


def regional_net_assets(region, asset_type, build_type, core_lut):
    """
    Return regional assets.

    """
    if asset_type in core_lut.keys():
        combined_key = '{}_{}'.format(region['GID_id'], build_type)
        if combined_key in core_lut[asset_type]:
            if asset_type == 'regional_edge':
                return core_lut[asset_type][combined_key]
            if asset_type == 'regional_node':
                return core_lut[asset_type][combined_key]
        else:
            return 0

    return 0


def core_net_assets(region, asset_type, build_type, core_lut):
    """
    Return all core assets.

    """
    if asset_type == 'core_edge':
        if asset_type in core_lut.keys():
            combined_key = '{}_{}'.format(region['GID_id'], build_type)
            if combined_key in core_lut[asset_type].keys():
                return core_lut[asset_type][combined_key]
            else:
                return 0
        else:
            return 0

    elif asset_type == 'core_node':
        if asset_type in core_lut.keys():
            combined_key = '{}_{}'.format(region['GID_id'], build_type)
            if combined_key in core_lut[asset_type].keys():
                return core_lut[asset_type][combined_key]
            else:
                return 0
        else:
            return 0

    else:
        print('Did not recognise core asset type {}'.format(asset_type))
        return 0


def calc_assets(region, option, asset_structure, i, new_backhaul, costs, build_type):
    """

    """
    backhaul = option['strategy'].split('_')[2]
    geotype = region['geotype'].split(' ')[0]

    if i <= new_backhaul:
        backhaul_quantity = 1
    else:
        backhaul_quantity = 0

    total_assets = []

    for asset_name1, quantity in asset_structure.items():

        if asset_name1 == 'backhaul' and backhaul_quantity == 0:
            continue

        if asset_name1 == 'site_rental':
            asset_name1 = asset_name1 + '_' + geotype

        if asset_name1 == 'backhaul':
            quantity, backhaul_name = estimate_backhaul_type(backhaul, quantity, geotype)
            cost_per_unit = costs[backhaul_name]
            asset_name1 = asset_name1 + '_' + backhaul_name
        else:
            cost_per_unit = costs[asset_name1]

        total_assets.append({
            'scenario': region['scenario'],
            'strategy': region['strategy'],
            'confidence': region['confidence'],
            'GID_id': region['GID_id'],
            'asset': asset_name1,
            'quantity': quantity,
            'cost_per_unit': cost_per_unit,
            'total_cost': quantity * cost_per_unit,
            'build_type': build_type,
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
