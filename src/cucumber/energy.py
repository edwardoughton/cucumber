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

        #get the distance between points sqrt(1/site density) / 2
        #dividing by 2 gets the distance from the site to the cell edge
        distance_km = math.sqrt(1/(decile['network_required_sites']/decile['area_km2']))/2
        
        baseline_net_handle = 'baseline' + '_' + decile['geotype']
        baseline_networks = country['networks'][baseline_net_handle]

        if decile['backhaul'] == 'wireless':
            if distance_km < 20:
                selected_backhaul = country['energy_wireless_small_kwh']
            elif distance_km < 40:
                selected_backhaul = country['energy_wireless_medium_kwh']
            else:
                selected_backhaul = country['energy_wireless_large_kwh']
        elif decile['backhaul'] == 'fiber':
            selected_backhaul = fiber_bh_kwh

        existing_site_energy_kwh = (
            (decile['total_existing_sites'] / decile['networks']) * 
            site_kwh * 24 * 365) 
        existing_backhaul_energy_kwh = (
            (math.floor(decile['backhaul_wireless'] / decile['networks']) * 
             wireless_bh_kwh * 24 * 365) + 
            (math.floor(decile['backhaul_fiber'] / decile['networks']) * 
            fiber_bh_kwh * 24 * 365)) 
        new_site_energy_kwh = (decile['network_new_sites'] * 
                               site_kwh * 24 * 365) 
        new_backhaul_energy_kwh = ((decile['backhaul_new'] * 
                                    selected_backhaul * 24 * 365)) 

        decile['network_existing_energy_kwh'] = (existing_site_energy_kwh + existing_backhaul_energy_kwh) 
        decile['network_new_energy_kwh'] = (new_site_energy_kwh + new_backhaul_energy_kwh) 

        output.append(decile)

        for energy_type, percentage in on_grid_mix.items():

            existing_energy_kwh = float(decile['network_existing_energy_kwh']) * percentage
            new_energy_kwh = float(decile['network_new_energy_kwh']) * percentage

            energy.append({
                'country_name': country['country_name'],
                'iso3': country['iso3'],
                'decile': decile['decile'],
                'population': decile['population_total'],  
                'area_km2': decile['area_km2'],        
                'population_km2': decile['population_km2'],
                'capacity': decile['capacity'],
                'generation': decile['generation'],
                'backhaul': decile['backhaul'],
                'energy_scenario': decile['energy_scenario'],
                'income': country['income'],
                'wb_region': country['wb_region'],
                'adb_region': country['adb_region'],
                'iea_classification': country['iea_classification'],
                'product': energy_type,
                'network_existing_energy_kwh': existing_energy_kwh,
                'network_new_energy_kwh': new_energy_kwh,
            })

    return output, energy

