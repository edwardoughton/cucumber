"""
Cost module

Author: Edward Oughton

Date: June 2021

"""
import math
from itertools import tee
import collections, functools, operator
import pandas as pd


def assess_cost(country, deciles):
    """
    Estimate emissions.

    Parameters
    ----------
    country : dict
        All country metadata.
    deciles : list of dicts
        Data for all deciles (one dict per decile).

    Returns
    -------
    deciles : list of dicts
        Data for all deciles (one dict per decile).

    """
    output = []

    for decile in deciles:

        #get the distance between points sqrt(1/site density) / 2
        #dividing by 2 gets the distance from the site to the cell edge
        distance_km = math.sqrt(1/(decile['network_required_sites']/decile['area_km2']))/2

        baseline_net_handle = 'baseline' + '_' + decile['geotype']
        baseline_networks = country['networks'][baseline_net_handle]

        if decile['backhaul'] == 'wireless':
            if distance_km < 20:
                selected_backhaul_cost = country['cost_wireless_small']
            elif distance_km < 40:
                selected_backhaul_cost = country['cost_wireless_medium']
            else:
                selected_backhaul_cost = country['cost_wireless_large']
        elif decile['backhaul'] == 'fiber':
            selected_backhaul_cost = country['cost_fiber_suburban_m'] * 1e3 * distance_km

        if decile['sharing_scenario'] =='passive':
            decile['network_cost_site_build_usd'] = (decile['network_new_sites'] * country['cost_site_build']) * (1 / decile['networks'])
        else:
            decile['network_cost_site_build_usd'] = (decile['network_new_sites'] * country['cost_site_build'])

        decile['network_cost_equipment_usd'] = (decile['network_new_sites'] * country['cost_equipment'])
        decile['network_cost_backhaul_usd'] = (decile['backhaul_new'] * selected_backhaul_cost)
        decile['network_cost_installation_usd'] = (decile['network_new_sites'] * country['cost_installation'])
        decile['network_cost_operation_and_maintenance_usd'] = (decile['network_new_sites'] * country['cost_operation_and_maintenance'])
        decile['network_cost_power_usd'] =  (decile['network_new_sites'] * country['cost_power'])

        decile['network_new_cost_usd'] = (
            decile['network_cost_equipment_usd'] + 
            decile['network_cost_backhaul_usd'] +
            decile['network_cost_site_build_usd'] +
            decile['network_cost_installation_usd'] + 
            decile['network_cost_operation_and_maintenance_usd'] +
            decile['network_cost_power_usd']  
        )
        
        #sites
        decile['total_required_sites'] = calc(decile, 'network_required_sites')
        decile['total_upgraded_sites'] = calc(decile, 'network_upgraded_sites')
        decile['total_new_sites'] = calc(decile, 'network_new_sites')
        
        #energy/emissions
        decile['total_existing_energy_kwh'] = calc(decile, 'network_existing_energy_kwh')
        decile['total_new_energy_kwh'] = calc(decile, 'network_new_energy_kwh')
        decile['total_existing_emissions_t_co2'] = calc(decile, 'network_existing_emissions_t_co2')
        decile['total_new_emissions_t_co2'] = calc(decile, 'network_new_emissions_t_co2')

        #costs
        decile['total_new_cost_usd'] = calc(decile, 'network_new_cost_usd')
        decile['total_cost_equipment_usd'] = calc(decile, 'network_cost_equipment_usd')
        decile['total_cost_backhaul_usd'] = calc(decile, 'network_cost_backhaul_usd')
        if decile['sharing_scenario'] =='passive':
            decile['total_cost_site_build_usd'] = decile['network_cost_site_build_usd']
        else:
            decile['total_cost_site_build_usd'] = calc(decile, 'network_cost_site_build_usd')
        decile['total_cost_installation_usd'] = calc(decile, 'network_cost_installation_usd')
        decile['total_cost_operation_and_maintenance_usd'] = calc(decile, 'network_cost_operation_and_maintenance_usd')
        decile['total_cost_power_usd'] = calc(decile, 'network_cost_power_usd')

        output.append(decile)

    return output


def calc(decile, metric):
    """

    """
    if metric in decile:

        value = decile[metric]

        if value == 0 or decile['smartphones_on_network'] == 0:
            return 0

        value_per_user = value / decile['smartphones_on_network']

        return value_per_user * decile['population_with_smartphones']

    else:

        return 0