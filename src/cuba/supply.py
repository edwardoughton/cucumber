"""
Optimize supply

Written by Ed Oughton.

Winter 2020

"""
import math
from itertools import tee
from operator import itemgetter

from cuba.assets import estimate_assets
from cuba.costs import find_cost


def estimate_supply(country, regions, capacity_lut, option,
    global_parameters, country_parameters,
    costs, ci, infra_sharing_options, cost_types
    ):
    """
    For each region, find the least-cost design and estimate
    the required investment for for the single network being modeled.

    Parameters
    ----------
    country : dict
        Country information.
    regions : list of dicts
        Data for all regions (one dict per region).
    capacity_lut : dict
        A dictionary containing the lookup capacities.
    sites_lut : dict
        A dictionary containing the sites lookup.
    option : dict
        Contains the scenario and strategy. The strategy string controls
        the strategy variants being tested in the model and is defined based
        on the type of technology generation, core and backhaul, and the
        strategy for infrastructure sharing, the number of networks in each
        geotype, spectrum and taxation.
    global_parameters : dict
        All global model parameters.
    country_parameters : dict
        All country specific parameters.
    costs : dict
        All equipment costs.
    core_lut : dict
        Contains the number of existing and required, core and regional assets.
    ci : int
        Confidence interval.
    infra_sharing_assets : dict
        Shared infra assets lookup by strategy (e.g. passive,
        active or srn).
    cost_types : dict
        Cost types lookup (e.g. capex, opex or both).

    Returns
    -------
    regions : list of dicts
        Data for all regions (one dict per region).

    """
    output_regions = []
    output_assets = {}

    for region in regions:

        region['scenario'] = option['scenario']
        region['strategy'] = option['strategy']
        region['confidence'] = ci

        region['mno_site_density'] = find_site_density(country, region, option,
            global_parameters, capacity_lut, ci)

        if region['mno_site_density'] > 0:

            region['total_sites_required'] = math.ceil(region['mno_site_density'] *
                region['area_km2'])

            region = estimate_site_upgrades(
                region,
                option['strategy'],
                country_parameters
            )

            region = estimate_backhaul_upgrades(
                region,
                option['strategy'],
                country_parameters
            )

        else:
            region['existing_mno_sites'] =  (
                region['total_estimated_sites'] /
                country_parameters['networks']['baseline' + '_' + region['geotype'].split(' ')[0]]
            )
            region['new_mno_sites'] = 0
            region['upgraded_mno_sites'] = 0
            region['backhaul_new'] = 0

        assets = estimate_assets(
            country,
            region,
            option,
            costs,
            global_parameters,
            country_parameters,
        )

        region = find_cost(
            region,
            assets,
            option,
            costs,
            global_parameters,
            country_parameters,
            infra_sharing_options,
            cost_types
        )

        output_regions.append(region)
        output_assets[region['decile']] = assets

    return output_regions, output_assets


def find_site_density(country, region, option, global_parameters,
    capacity_lut, ci):
    """
    For a given region, estimate the number of needed sites.

    Parameters
    ----------
    country : dict
        Country metadata. 
    region : dicts
        Data for a single region.
    option : dict
        Contains the scenario and strategy. The strategy string controls
        the strategy variants being tested in the model and is defined based
        on the type of technology generation, core and backhaul, and the
        strategy for infrastructure sharing, the number of networks in each
        geotype, spectrum and taxation.
    global_parameters : dict
        All global model parameters.
    capacity_lut : dict
        A dictionary containing the lookup capacities.
    ci : int
        Confidence interval.

    Return
    ------
    site_density : float
        Estimated site density.

    """
    demand = region['demand_mbps_km2']
    geotype = region['geotype'].split(' ')[0]
    ant_type = 'macro'
    generation = option['strategy'].split('_')[0]
    all_frequencies = find_frequencies(country)
    frequencies = all_frequencies[generation]
    target = find_target(geotype, option)

    if target == 0:
        return 0

    ci = str(ci)
    unique_densities = set()

    capacity = 0

    for item in frequencies:

        frequency = str(item['frequency'])
        bandwidth = str(item['bandwidth'].split('x')[1])

        density_capacities = lookup_capacity(
            capacity_lut,
            geotype,
            ant_type,
            frequency,
            generation,
            ci
        )

        for item in density_capacities:
            site_density, capacity = item
            unique_densities.add(site_density)

    density_lut = []

    for density in list(unique_densities):

        capacity = 0

        for item in frequencies:

            frequency = str(item['frequency'])
            channels, bandwidth = item['bandwidth'].split('x')
            channels, bandwidth = float(channels), float(bandwidth)

            if channels == 1: #allocate downlink channel width when using TDD
                downlink = float(global_parameters['tdd_dl_to_ul'].split(':')[0])
                bandwidth = bandwidth * (downlink / 100)

            density_capacities = lookup_capacity(
                capacity_lut,
                geotype,
                ant_type,
                frequency,
                generation,
                ci
            )

            for density_capacity in density_capacities:

                if density_capacity[0] == density:
                    capacity += density_capacity[1]

        density_lut.append((density, capacity))

    density_lut = sorted(density_lut, key=lambda tup: tup[0])

    max_density, max_capacity = density_lut[-1]
    min_density, min_capacity = density_lut[0]

    if demand > max_capacity:

        return max_density

    elif demand < min_capacity:

        return min_density

    else:

        for a, b in pairwise(density_lut):

            lower_density, lower_capacity  = a
            upper_density, upper_capacity  = b

            if lower_capacity <= demand < upper_capacity:

                site_density = interpolate(
                    lower_capacity, lower_density,
                    upper_capacity, upper_density,
                    demand
                )

                return site_density


def find_frequencies(country):
    """
    Lookup frequency portfolio by country income level.

    """
    if country['income'] == 'HIC':
        return {
            '4G': [
                {
                    'frequency': 800,
                    'bandwidth': '2x10',
                },
                {
                    'frequency': 1800,
                    'bandwidth': '2x10',
                },
                {
                    'frequency': 2600,
                    'bandwidth': '2x10',
                },
            ],
            '5G': [
                {
                    'frequency': 700,
                    'bandwidth': '2x10',
                },
                {
                    'frequency': 3500,
                    'bandwidth': '1x40',
                },
            ],
        }
    elif country['income'] == 'UMIC' or country['income'] == 'LMIC':
        return {
            '4G': [
                {
                    'frequency': 800,
                    'bandwidth': '2x10',
                },
                {
                    'frequency': 2600,
                    'bandwidth': '2x10',
                },
            ],
            '5G': [
                {
                    'frequency': 700,
                    'bandwidth': '2x10',
                },
                {
                    'frequency': 3500,
                    'bandwidth': '1x40',
                },
            ],
        }
    elif country['income'] == 'LIC':
        return {
            '4G': [
                {
                    'frequency': 800,
                    'bandwidth': '2x10',
                },
            ],
            '5G': [
                {
                    'frequency': 700,
                    'bandwidth': '2x10',
                },
            ],
        }
    else:
        print('Did not recognize country income level')
        print('Using mean spectrum portfolio size')
        return {
            '4G': [
                {
                    'frequency': 800,
                    'bandwidth': '2x10',
                },
                {
                    'frequency': 2600,
                    'bandwidth': '2x10',
                },
            ],
            '5G': [
                {
                    'frequency': 700,
                    'bandwidth': '2x10',
                },
                {
                    'frequency': 3500,
                    'bandwidth': '1x40',
                },
            ],
        }

    return


def find_target(geotype, option):
    """
    Find speed target.

    """
    if geotype == 'urban':
        target = int(option['scenario'].split('_')[1])
    elif geotype == 'suburban':
        target = int(option['scenario'].split('_')[2])
    elif geotype == 'rural':
        target = int(option['scenario'].split('_')[3])
    else:
        print('Did not recognize geotype when trying to find speed target')

    return target


def lookup_capacity(capacity_lut, env, ant_type, frequency,
    generation, ci):
    """
    Use lookup table to find the combination of spectrum bands
    which meets capacity by clutter environment geotype, frequency,
    bandwidth, technology generation and site density.

    Parameters
    ----------
    capacity_lut : dict
        A dictionary containing the lookup capacities.
    env : string
        The settlement type e.g. urban, suburban or rural.
    ant_type : string
        The antenna type, such as a macro cell or micro cell.
    frequency : string
        The frequency band in Megahertz.
    generation : string
        The cellular generation such as 4G or 5G.
    ci : int
        Confidence interval.

    Returns
    -------
    site_densities_to_capacities : list of tuples
        Returns a list of site density to capacity tuples.

    """
    if (ant_type, frequency, generation, ci) not in capacity_lut:
        raise KeyError("Combination %s not found in lookup table",
                       (ant_type, frequency, generation, ci))

    density_capacities = capacity_lut[
        (ant_type,  frequency, generation, ci)
    ]

    return density_capacities


def interpolate(x0, y0, x1, y1, x):
    """
    Linear interpolation between two values.
    """
    y = (y0 * (x1 - x) + y1 * (x - x0)) / (x1 - x0)

    return y


def pairwise(iterable):
    """
    Return iterable of 2-tuples in a sliding window.
    >>> list(pairwise([1,2,3,4]))
    [(1,2),(2,3),(3,4)]
    """
    a, b = tee(iterable)
    next(b, None)

    return zip(a, b)


def estimate_site_upgrades(region, strategy, country_parameters):
    """
    Estimate the number of greenfield sites and brownfield upgrades for the
    single network being modeled.

    Parameters
    ----------
    region : dict
        Contains all regional data.
    strategy : dict
        Controls the strategy variants being tested in the model and is
        defined based on the type of technology generation, core and
        backhaul, and the level of sharing, subsidy, spectrum and tax.
    country_parameters : dict
        All country specific parameters.

    Returns
    -------
    region : dict
        Contains all regional data.

    """
    generation = strategy.split('_')[0]
    geotype = region['geotype'].split(' ')[0]
    sharing = strategy.split('_')[3]

    #get the number of networks in the area
    networks = country_parameters['networks'][sharing + '_' + geotype]

    region['existing_mno_sites'] = math.ceil(region['total_estimated_sites'] / networks)

    #get the number of existing 4G sites
    existing_4G_sites = math.ceil(region['total_estimated_sites_4G'] / networks)

    if region['total_sites_required'] > region['existing_mno_sites']:
        region['new_mno_sites'] = (int(round(region['total_sites_required'] -
            region['existing_mno_sites'])))
        if region['existing_mno_sites'] > 0:
            if generation == '4G' and existing_4G_sites > 0 :
                region['upgraded_mno_sites'] = (region['existing_mno_sites'] -
                    existing_4G_sites)
            else:
                region['upgraded_mno_sites'] = region['existing_mno_sites']
        else:
            region['upgraded_mno_sites'] = 0

    else:
        region['new_mno_sites'] = 0
        if generation == '4G' and existing_4G_sites > 0 :
            to_upgrade = region['total_sites_required'] - existing_4G_sites
            region['upgraded_mno_sites'] = to_upgrade if to_upgrade >= 0 else 0
        else:
            region['upgraded_mno_sites'] = region['total_sites_required']

    return region


def estimate_backhaul_upgrades(region, strategy, country_parameters):
    """
    Estimates the number of backhaul links requiring upgrades for the
    single network being modeled.

    Parameters
    ----------
    region : dict
        Contains all regional data.
    strategy : dict
        The strategy string controls the strategy variants being tested in the
        model and is defined based on the type of technology generation, core
        and backhaul, and the level of sharing, subsidy, spectrum and tax.
    country_parameters : dict
        All country specific parameters.

    Returns
    -------
    region : dict
        Contains all regional data.
        
    """
    backhaul = strategy.split('_')[2]
    geotype = region['geotype'].split(' ')[0]
    networks = country_parameters['networks']['baseline' + '_' + geotype]
    all_mno_sites = (region['new_mno_sites'] + region['upgraded_mno_sites']) # networks

    if backhaul == 'fiber':

        region['backhaul_existing'] = region['backhaul_fiber'] / networks

        if region['backhaul_existing'] < all_mno_sites:
            region['backhaul_new'] =  math.ceil(all_mno_sites - region['backhaul_existing'])
        else:
            region['backhaul_new'] = 0

    elif backhaul == 'wireless':

        region['backhaul_existing'] = (region['backhaul_wireless'] +
            region['backhaul_fiber']) / networks

        if region['backhaul_existing'] < all_mno_sites:
            region['backhaul_new'] =  math.ceil(all_mno_sites - region['backhaul_existing'])
        else:
            region['backhaul_new'] = 0

    return region
