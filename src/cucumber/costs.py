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

        baseline_net_handle = 'baseline' + '_' + decile['geotype']
        baseline_networks = country['networks'][baseline_net_handle]

        if decile['sharing_scenario'] in ['active', 'srn']:
            net_handle = decile['sharing_scenario'] + '_' + decile['geotype']
            networks = country['networks'][net_handle]
            network_division = (networks/baseline_networks)
        else:
            network_division = 1

        # if decile['sharing_scenario'] in ['baseline', 'passive']:
        #     decile['network_cost_equipment_usd'] = (decile['network_new_sites'] * country['cost_equipment'])
        #     decile['network_cost_site_build_usd'] = (decile['network_new_sites'] * country['cost_site_build'])
        #     decile['network_cost_installation_usd'] = (decile['network_new_sites'] * country['cost_installation'])
        #     decile['network_cost_operation_and_maintenance_usd'] = (decile['network_new_sites'] * country['cost_operation_and_maintenance'])
        #     decile['network_cost_power_usd'] =  (decile['network_new_sites'] * country['cost_power'])

        # elif decile['sharing_scenario'] == 'srn':
        #     if decile['geotype'] == 'urban' or decile['geotype'] == 'suburban':
        #         decile['network_cost_equipment_usd'] = (decile['network_new_sites'] * country['cost_equipment'])
        #         decile['network_cost_site_build_usd'] = (decile['network_new_sites'] * country['cost_site_build'])
        #         decile['network_cost_installation_usd'] = (decile['network_new_sites'] * country['cost_installation'])
        #         decile['network_cost_operation_and_maintenance_usd'] = (decile['network_new_sites'] * country['cost_operation_and_maintenance'])
        #         decile['network_cost_power_usd'] =  (decile['network_new_sites'] * country['cost_power'])
        #     else:   
        #         decile['network_cost_equipment_usd'] = (decile['network_new_sites'] * country['cost_equipment']) * network_division
        #         decile['network_cost_site_build_usd'] = (decile['network_new_sites'] * country['cost_site_build']) * network_division
        #         decile['network_cost_installation_usd'] = (decile['network_new_sites'] * country['cost_installation']) * network_division
        #         decile['network_cost_operation_and_maintenance_usd'] = (decile['network_new_sites'] * country['cost_operation_and_maintenance']) * network_division
        #         decile['network_cost_power_usd'] =  (decile['network_new_sites'] * country['cost_power']) * network_division

        # elif decile['sharing_scenario'] == 'active':
        #     decile['network_cost_equipment_usd'] = (decile['network_new_sites'] * country['cost_equipment']) * network_division
        #     decile['network_cost_site_build_usd'] = (decile['network_new_sites'] * country['cost_site_build']) * network_division
        #     decile['network_cost_installation_usd'] = (decile['network_new_sites'] * country['cost_installation']) * network_division
        #     decile['network_cost_operation_and_maintenance_usd'] = (decile['network_new_sites'] * country['cost_operation_and_maintenance']) * network_division
        #     decile['network_cost_power_usd'] =  (decile['network_new_sites'] * country['cost_power']) * network_division
        
        # else:
        #     print('Did not reognize sharing scenario')

        if decile['sharing_scenario'] =='passive':
            decile['network_cost_site_build_usd'] = (decile['network_new_sites'] * country['cost_site_build']) * (1 / decile['networks'])
        else:
            decile['network_cost_site_build_usd'] = (decile['network_new_sites'] * country['cost_site_build'])
        # print(decile['sharing_scenario'], round(decile['network_cost_site_build_usd']/1e9,3), (1/decile['networks']))
        decile['network_cost_equipment_usd'] = (decile['network_new_sites'] * country['cost_equipment'])
        decile['network_cost_installation_usd'] = (decile['network_new_sites'] * country['cost_installation'])
        decile['network_cost_operation_and_maintenance_usd'] = (decile['network_new_sites'] * country['cost_operation_and_maintenance'])
        decile['network_cost_power_usd'] =  (decile['network_new_sites'] * country['cost_power'])

        decile['network_new_cost_usd'] = (
            decile['network_cost_equipment_usd'] + 
            decile['network_cost_site_build_usd'] +
            decile['network_cost_installation_usd'] + 
            decile['network_cost_operation_and_maintenance_usd'] +
            decile['network_cost_power_usd']  
        )
        # print(decile['sharing_scenario'],decile['network_new_cost_usd']/1e9)
        ms = 100 / decile['networks']
        
        #sites
        decile['total_required_sites'] = calc(decile, 'network_required_sites', ms)
        decile['total_upgraded_sites'] = calc(decile, 'network_upgraded_sites', ms)
        decile['total_new_sites'] = calc(decile, 'network_new_sites', ms)
        
        #energy/emissions
        decile['total_existing_energy_kwh'] = calc(decile, 'network_existing_energy_kwh', ms)
        decile['total_new_energy_kwh'] = calc(decile, 'network_new_energy_kwh', ms)
        decile['total_existing_emissions_t_co2'] = calc(decile, 'network_existing_emissions_t_co2', ms)
        decile['total_new_emissions_t_co2'] = calc(decile, 'network_new_emissions_t_co2', ms)

        #costs
        decile['total_new_cost_usd'] = calc(decile, 'network_new_cost_usd', ms)
        decile['total_cost_equipment_usd'] = calc(decile, 'network_cost_equipment_usd', ms)
        decile['total_cost_site_build_usd'] = calc(decile, 'network_cost_site_build_usd', ms)
        decile['total_cost_installation_usd'] = calc(decile, 'network_cost_installation_usd', ms)
        decile['total_cost_operation_and_maintenance_usd'] = calc(decile, 'network_cost_operation_and_maintenance_usd', ms)
        decile['total_cost_power_usd'] = calc(decile, 'network_cost_power_usd', ms)

        output.append(decile)

    return output


def calc(decile, metric, ms):
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