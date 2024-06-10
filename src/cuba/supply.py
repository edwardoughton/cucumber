"""
Optimize supply

Written by Ed Oughton.

Winter 2020

"""
import math
from itertools import tee
from operator import itemgetter


def estimate_supply(country, deciles, capacity_lut):
    """
    Estimate supply metrics.

    Parameters
    ----------
    country : dict
        All country metadata.
    deciles : list of dicts
        Data for all deciles (one dict per decile).
    capacity_lut : dict
        A dictionary containing the lookup capacities.

    Returns
    -------
    deciles : list of dicts
        Data for all deciles (one dict per decile).

    """
    output = []

    for decile in deciles:

        total_site_density = find_site_density(
            country, 
            decile, 
            capacity_lut
        )

        if decile['total_existing_sites'] > 0:

            total_required_sites = math.ceil(
                total_site_density *
                decile['area_km2']
            )

            total_new_sites = (
                total_required_sites - 
                decile['total_existing_sites']
            )

            if total_new_sites > 0:
                decile['total_new_sites'] = total_new_sites
            else:
                decile['total_new_sites'] = 0
        else:
            decile['total_new_sites'] = 0

            # print(decile['total_estimated_sites'], decile['total_sites_required'])
            # decile = estimate_site_upgrades(
            #     decile,
            #     option['strategy'],
            #     country_parameters
            # )

            # decile = estimate_backhaul_upgrades(
            #     decile,
            #     option['strategy'],
            #     country_parameters
            # )

        # else:
        #     decile['existing_mno_sites'] =  (
        #         decile['total_estimated_sites'] /
        #         country_parameters['networks']['baseline' + '_' + decile['geotype'].split(' ')[0]]
        #     )
        #     decile['new_mno_sites'] = 0
        #     decile['upgraded_mno_sites'] = 0
        #     decile['backhaul_new'] = 0

        # assets = estimate_assets(
        #     country,
        #     decile,
        #     option,
        #     costs,
        #     global_parameters,
        #     country_parameters,
        # )

        # decile = find_cost(
        #     decile,
        #     assets,
        #     option,
        #     costs,
        #     global_parameters,
        #     country_parameters,
        #     infra_sharing_options,
        #     cost_types
        # )

        output.append(decile)
        # output_assets[decile['decile']] = assets

    return output


def find_site_density(country, decile, capacity_lut):
    """
    For a given decile, estimate the number of needed sites.

    Parameters
    ----------
    country : dict
        Country metadata. 
    decile : dicts
        Data for a single decile.
    capacity_lut : dict
        A dictionary containing the lookup capacities.

    Return
    ------
    site_density : float
        Estimated site density.

    """
    demand = decile['demand_mbps_km2']
    geotype = decile['geotype'].split(' ')[0]
    ant_type = 'macro'
    generation = decile['generation']#.split('_')[0]
    all_frequencies = find_frequencies(country)
    frequencies = all_frequencies[generation]
    target_gb = decile['capacity'] #30 #find_target(geotype, option)

    if target_gb == 0:
        return 0

    ci = '90'#str(ci)
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
                downlink = 0.8 #float(global_parameters['tdd_dl_to_ul'].split(':')[0])
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


# def find_target(geotype, option):
#     """
#     Find speed target.

#     """
#     if geotype == 'urban':
#         target = int(option['scenario'].split('_')[1])
#     elif geotype == 'suburban':
#         target = int(option['scenario'].split('_')[2])
#     elif geotype == 'rural':
#         target = int(option['scenario'].split('_')[3])
#     else:
#         print('Did not recognize geotype when trying to find speed target')

#     return target


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


def estimate_site_upgrades(decile, strategy, country_parameters):
    """
    Estimate the number of greenfield sites and brownfield upgrades for the
    single network being modeled.

    Parameters
    ----------
    decile : dict
        Contains all decileal data.
    strategy : dict
        Controls the strategy variants being tested in the model and is
        defined based on the type of technology generation, core and
        backhaul, and the level of sharing, subsidy, spectrum and tax.
    country_parameters : dict
        All country specific parameters.

    Returns
    -------
    decile : dict
        Contains all decileal data.

    """
    generation = strategy.split('_')[0]
    geotype = decile['geotype'].split(' ')[0]
    sharing = strategy.split('_')[3]

    #get the number of networks in the area
    networks = country_parameters['networks'][sharing + '_' + geotype]

    decile['existing_mno_sites'] = math.ceil(decile['total_estimated_sites'] / networks)

    #get the number of existing 4G sites
    existing_4G_sites = math.ceil(decile['total_estimated_sites_4G'] / networks)

    if decile['total_sites_required'] > decile['existing_mno_sites']:
        decile['new_mno_sites'] = (int(round(decile['total_sites_required'] -
            decile['existing_mno_sites'])))
        if decile['existing_mno_sites'] > 0:
            if generation == '4G' and existing_4G_sites > 0 :
                decile['upgraded_mno_sites'] = (decile['existing_mno_sites'] -
                    existing_4G_sites)
            else:
                decile['upgraded_mno_sites'] = decile['existing_mno_sites']
        else:
            decile['upgraded_mno_sites'] = 0

    else:
        decile['new_mno_sites'] = 0
        if generation == '4G' and existing_4G_sites > 0 :
            to_upgrade = decile['total_sites_required'] - existing_4G_sites
            decile['upgraded_mno_sites'] = to_upgrade if to_upgrade >= 0 else 0
        else:
            decile['upgraded_mno_sites'] = decile['total_sites_required']

    return decile


def estimate_backhaul_upgrades(decile, strategy, country_parameters):
    """
    Estimates the number of backhaul links requiring upgrades for the
    single network being modeled.

    Parameters
    ----------
    decile : dict
        Contains all decileal data.
    strategy : dict
        The strategy string controls the strategy variants being tested in the
        model and is defined based on the type of technology generation, core
        and backhaul, and the level of sharing, subsidy, spectrum and tax.
    country_parameters : dict
        All country specific parameters.

    Returns
    -------
    decile : dict
        Contains all decileal data.
        
    """
    backhaul = strategy.split('_')[2]
    geotype = decile['geotype'].split(' ')[0]
    networks = country_parameters['networks']['baseline' + '_' + geotype]
    all_mno_sites = (decile['new_mno_sites'] + decile['upgraded_mno_sites']) # networks

    if backhaul == 'fiber':

        decile['backhaul_existing'] = decile['backhaul_fiber'] / networks

        if decile['backhaul_existing'] < all_mno_sites:
            decile['backhaul_new'] =  math.ceil(all_mno_sites - decile['backhaul_existing'])
        else:
            decile['backhaul_new'] = 0

    elif backhaul == 'wireless':

        decile['backhaul_existing'] = (decile['backhaul_wireless'] +
            decile['backhaul_fiber']) / networks

        if decile['backhaul_existing'] < all_mno_sites:
            decile['backhaul_new'] =  math.ceil(all_mno_sites - decile['backhaul_existing'])
        else:
            decile['backhaul_new'] = 0

    return decile
