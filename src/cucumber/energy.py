import math 
"""
Energy Assessment Module

Written by Ed Oughton

June 2021

"""

def assess_energy(country, deciles, on_grid_mix):
    """
    Estimate energy consumption.

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
    energy = []
    
    site_kwh = country['energy_equipment_kwh'] #1 #kwh per site
    wireless_bh_kwh = country['energy_wireless_medium_kwh'] #0.5 #kwh per link
    fiber_bh_kwh = country['energy_fiber_kwh'] #0.01 #kwh per link
    
    for decile in deciles:

        baseline_net_handle = 'baseline' + '_' + decile['geotype']
        baseline_networks = country['networks'][baseline_net_handle]

        # if decile['sharing_scenario'] in ['active', 'srn']:
        #     net_handle = decile['sharing_scenario'] + '_' + decile['geotype']
        #     networks = country['networks'][net_handle]
        #     network_division = (networks/baseline_networks)

        # else:
        #     network_division = 1

        if decile['backhaul'] == 'wireless':
            selected_backhaul = wireless_bh_kwh
        elif decile['backhaul'] == 'fiber':
            selected_backhaul = fiber_bh_kwh
 
        # if decile['sharing_scenario'] in ['baseline', 'passive']:
        #     existing_site_energy_kwh = (decile['network_existing_sites'] * site_kwh * 24 * 365) #kwh per site
        #     existing_backhaul_energy_kwh = ((decile['backhaul_wireless'] * wireless_bh_kwh * 24 * 365) + (decile['backhaul_fiber'] * fiber_bh_kwh * 24 * 365)) #kwh per site
        #     new_site_energy_kwh = (decile['network_new_sites'] * site_kwh * 24 * 365) #kwh per site
        #     new_backhaul_energy_kwh = ((decile['backhaul_new'] * selected_backhaul * 24 * 365))

        # elif decile['sharing_scenario'] == 'srn':
        #     if decile['geotype'] == 'urban' or decile['geotype'] == 'suburban':
        #         existing_site_energy_kwh = (decile['network_existing_sites'] * site_kwh * 24 * 365) #kwh per site
        #         existing_backhaul_energy_kwh = ((decile['backhaul_wireless'] * wireless_bh_kwh * 24 * 365) + (decile['backhaul_fiber'] * fiber_bh_kwh * 24 * 365)) #kwh per site
        #         new_site_energy_kwh = (decile['network_new_sites'] * site_kwh * 24 * 365) #kwh per site
        #         new_backhaul_energy_kwh = ((decile['backhaul_new'] * selected_backhaul * 24 * 365))
        #     else:
        #         existing_site_energy_kwh = (decile['network_existing_sites'] * site_kwh * 24 * 365) * network_division #kwh per site
        #         existing_backhaul_energy_kwh = ((decile['backhaul_wireless'] * wireless_bh_kwh * 24 * 365) + (decile['backhaul_fiber'] * fiber_bh_kwh * 24 * 365)) * network_division #kwh per site
        #         new_site_energy_kwh = (decile['network_new_sites'] * site_kwh * 24 * 365) * network_division #kwh per site
        #         new_backhaul_energy_kwh = ((decile['backhaul_new'] * selected_backhaul * 24 * 365)) * network_division

        # elif decile['sharing_scenario'] == 'active':
        #     existing_site_energy_kwh = (decile['network_existing_sites'] * site_kwh * 24 * 365) * network_division #kwh per site
        #     existing_backhaul_energy_kwh = ((decile['backhaul_wireless'] * wireless_bh_kwh * 24 * 365) + (decile['backhaul_fiber'] * fiber_bh_kwh * 24 * 365)) * network_division #kwh per site
        #     new_site_energy_kwh = (decile['network_new_sites'] * site_kwh * 24 * 365) * network_division #kwh per site
        #     new_backhaul_energy_kwh = ((decile['backhaul_new'] * selected_backhaul * 24 * 365)) * network_division

        # else:
        #     print('Did not reognize sharing scenario')
        # print(country['operators'])
        existing_site_energy_kwh = ((decile['total_existing_sites'] / decile['networks']) * site_kwh * 24 * 365) #* network_division #kwh per site
        existing_backhaul_energy_kwh = ((math.floor(decile['backhaul_wireless'] / decile['networks']) * wireless_bh_kwh * 24 * 365) + (math.floor(decile['backhaul_fiber'] / decile['networks']) * fiber_bh_kwh * 24 * 365)) #* network_division #kwh per site
        new_site_energy_kwh = (decile['network_new_sites'] * site_kwh * 24 * 365) #* network_division #kwh per site
        new_backhaul_energy_kwh = ((decile['backhaul_new'] * selected_backhaul * 24 * 365)) #* network_division

        decile['network_existing_energy_kwh'] = (existing_site_energy_kwh + existing_backhaul_energy_kwh) 
        decile['network_new_energy_kwh'] = (new_site_energy_kwh + new_backhaul_energy_kwh) 

        output.append(decile)

        for energy_type, percentage in on_grid_mix.items():

            existing_energy_kwh = round(
                float(decile['network_existing_energy_kwh']) * 
                percentage, 3
            )
            new_energy_kwh = round(
                float(decile['network_new_energy_kwh']) * 
                percentage, 3
            )

            energy.append({
                'country_name': country['country_name'],
                'iso3': country['iso3'],
                'decile': decile['decile'],
                # 'population': decile['population_total'],  
                # 'area_km2': decile['area_km2'],        
                # 'population_km2': decile['population_km2'],
                'capacity': decile['capacity'],
                'generation': decile['generation'],
                'backhaul': decile['backhaul'],
                'energy_scenario': decile['energy_scenario'],
                'income': country['income'],
                'wb_region': country['wb_region'],
                'iea_classification': country['iea_classification'],
                'product': energy_type,
                'network_existing_energy_kwh': existing_energy_kwh,
                'network_new_energy_kwh': new_energy_kwh,
            })

    return output, energy

